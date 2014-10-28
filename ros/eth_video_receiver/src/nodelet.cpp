#include <boost/bind.hpp>

#include <nodelet/nodelet.h>
#include <pluginlib/class_list_macros.h>
#include <ros/ros.h>
#include <sensor_msgs/Image.h>
#include <sensor_msgs/CameraInfo.h>
#include <sensor_msgs/image_encodings.h>

#include <iostream>
#include <boost/array.hpp>
#include <boost/asio.hpp>
#include <boost/thread.hpp>
#include <boost/make_shared.hpp>

using boost::asio::ip::udp;

namespace eth_video_receiver {

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
public:
  NodeImpl(boost::function<const std::string&()> getName,
  ros::NodeHandle * nhp,
  ros::NodeHandle * private_nhp) :
    getName_(getName),
    nh_(*nhp),
    private_nh_(*private_nhp),
    socket_(io_service_, udp::v4()) {
    
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
      boost::shared_ptr<sensor_msgs::CameraInfo> msg2p = boost::make_shared<sensor_msgs::CameraInfo>();
      msg2p->header = msgp_->header;
      msg2p->height = msgp_->height;
      msg2p->width = msgp_->width;
      info_pub_.publish(msg2p);
      image_pub_.publish(msgp_);
      msgp_.reset();
    }
    
    if(!msgp_) {
      msgp_ = boost::make_shared<sensor_msgs::Image>();
      msgp_->header.frame_id = "/camera";
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
