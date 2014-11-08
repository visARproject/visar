#include <boost/bind.hpp>

#include <nodelet/nodelet.h>
#include <pluginlib/class_list_macros.h>
#include <ros/ros.h>
#include <sensor_msgs/Image.h>
#include <sensor_msgs/CameraInfo.h>
#include <sensor_msgs/image_encodings.h>
#include <camera_info_manager/camera_info_manager.h>

#include <iostream>
#include <boost/array.hpp>
#include <boost/asio.hpp>
#include <boost/thread.hpp>
#include <boost/make_shared.hpp>

using boost::asio::ip::udp;

namespace eth_video_receiver {


void fail(std::string const &error_string) {
  throw std::runtime_error(error_string);
}
template<typename FirstType, typename SecondType, typename... MoreTypes>
void fail(FirstType first, SecondType second, MoreTypes... more) {
  std::ostringstream ss;
  ss << first << second;
  return fail(ss.str(), more...);
}

template<typename... ErrorDescTypes>
void require(bool cond, ErrorDescTypes... error_desc) {
  if(!cond) {
    fail(error_desc...);
  }
}


template<typename T>
bool _getParam(ros::NodeHandle &nh, const std::string &name, T &res) {
  return nh.getParam(name, res);
}
template<>
bool _getParam(ros::NodeHandle &nh, const std::string &name, ros::Duration &res) {
  double x; if(!nh.getParam(name, x)) return false;
  res = ros::Duration(x); return true;
}
template<>
bool _getParam(ros::NodeHandle &nh, const std::string &name, unsigned int &res) {
  int x; if(!nh.getParam(name, x)) return false;
  if(x < 0) {
    fail("param ", name, " must be >= 0");
  }
  res = static_cast<unsigned int>(x); return true;
}

template<typename T>
T getParam(ros::NodeHandle &nh, std::string name) {
  T res;
  require(_getParam(nh, name, res), "param ", name, " required");
  return res;
}
template<typename T>
T getParam(ros::NodeHandle &nh, std::string name, T default_value) {
  T res;
  if(!_getParam(nh, name, res)) {
    return default_value;
  }
  return res;
}



uint32_t read_be_uint32(uint8_t const * d) {
  return (d[0] << 24) | (d[1] << 16) | (d[2] << 8) | d[3];
}

class NodeImpl {
  boost::function<const std::string&()> getName_;
  ros::NodeHandle & nh_;
  ros::NodeHandle & private_nh_;
  ros::Publisher image_pub_;
  ros::Publisher info_pub_;
  boost::thread thinker_thread_;
  boost::asio::io_service io_service_;
  udp::socket socket_;
  udp::endpoint remote_endpoint_;
  boost::array<uint8_t, 1500> recv_buffer_;
  size_t const HEIGHT = 1200;
  size_t const WIDTH = 1600;
  bool seq_set = false;
  boost::shared_ptr<sensor_msgs::Image> msgp_;
  volatile bool run_;
  camera_info_manager::CameraInfoManager cinfo_;
  std::string frame_id_;
public:
  NodeImpl(boost::function<const std::string&()> getName,
  ros::NodeHandle * nhp,
  ros::NodeHandle * private_nhp) :
    getName_(getName),
    nh_(*nhp),
    private_nh_(*private_nhp),
    socket_(io_service_, udp::v4()),
    cinfo_(nh_,
      getParam<std::string>(private_nh_, "camera_name", "eth_video_camera"),
      getParam<std::string>(private_nh_, "camera_info_url", "")),
    frame_id_(getParam<std::string>(private_nh_, "frame_id")) {
    
    boost::asio::socket_base::broadcast option(true);
    socket_.set_option(option);
    // XXX try replacing any with broadcast
    socket_.bind(udp::endpoint(boost::asio::ip::address_v4::any(), 5185));
    
    image_pub_ = nh_.advertise<sensor_msgs::Image>("image_raw", 10);
    info_pub_ = nh_.advertise<sensor_msgs::CameraInfo>("camera_info", 10);
    run_ = true;
    thinker_thread_ = boost::thread([this]() {
      while(run_) {
        boost::system::error_code error;
        std::size_t bytes_transferred = socket_.receive_from(
          boost::asio::buffer(recv_buffer_), remote_endpoint_,
          0, error);
        
        if(!error) {
          handle_packet(bytes_transferred);
        }
      }
    });
  }
  
  void handle_packet(std::size_t bytes_transferred) {
    if(bytes_transferred != 812) {
      std::cout << "wrong size" << std::endl;
      return;
    }
    
    uint32_t frame_count = read_be_uint32(&recv_buffer_[0]);
    uint32_t row = read_be_uint32(&recv_buffer_[4]);
    uint8_t side = read_be_uint32(&recv_buffer_[8]);
    uint8_t const * data = &recv_buffer_[12];
    
    if(row >= HEIGHT) {
      std::cout << "wrong row" << std::endl;
      return;
    }
    if(side >= 2) {
      std::cout << "wrong side" << std::endl;
      return;
    }
    
    if(msgp_ && seq_set && frame_count != msgp_->header.seq && msgp_->header.seq - frame_count > 10) {
      boost::shared_ptr<sensor_msgs::CameraInfo> msg2p = boost::make_shared<sensor_msgs::CameraInfo>(cinfo_.getCameraInfo());
      msg2p->header = msgp_->header;
      info_pub_.publish(msg2p);
      image_pub_.publish(msgp_);
      msgp_.reset();
    }
    
    if(!msgp_) {
      msgp_ = boost::make_shared<sensor_msgs::Image>();
      msgp_->header.frame_id = frame_id_;
      msgp_->height = HEIGHT;
      msgp_->width = WIDTH;
      msgp_->encoding = sensor_msgs::image_encodings::BAYER_RGGB8;
      msgp_->is_bigendian = false;
      msgp_->step = WIDTH;
      msgp_->data.resize(msgp_->step*HEIGHT);
    }
    
    msgp_->header.seq = frame_count;
    seq_set = true;
    msgp_->header.stamp = ros::Time::now();
    for(size_t i = 0; i < WIDTH/2; i++) {
      msgp_->data[row*msgp_->step + side * (WIDTH/2) + i] = data[i];
    }
  }
  
  ~NodeImpl() {
    run_ = false;
    thinker_thread_.join();
  }
};

class Nodelet : public nodelet::Nodelet {
public:
  Nodelet() { }
  
  virtual void onInit() {
    try {
      nodeimpl = boost::in_place(boost::bind(&Nodelet::getName, this),
        &getNodeHandle(), &getPrivateNodeHandle());
    } catch(std::exception const & exc) {
      std::cout << "caught " << exc.what() << std::endl;
      throw std::runtime_error("caught exception");
    }
  }

private:
  boost::optional<NodeImpl> nodeimpl;
};
PLUGINLIB_DECLARE_CLASS(eth_video_receiver, nodelet, eth_video_receiver::Nodelet, nodelet::Nodelet);


}
