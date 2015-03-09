#include <boost/bind.hpp>
#include <sys/socket.h>
#include <errno.h>
#include <netinet/ip.h>

#include <nodelet/nodelet.h>
#include <pluginlib/class_list_macros.h>
#include <ros/ros.h>
#include <sensor_msgs/Image.h>
#include <sensor_msgs/CameraInfo.h>
#include <sensor_msgs/image_encodings.h>
#include <camera_info_manager/camera_info_manager.h>

#include <iostream>
#include <boost/array.hpp>
#include <boost/thread.hpp>
#include <boost/make_shared.hpp>

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


void throw_errno(std::string const & process) {
    int e = errno;
    char buf[1000];
    errno = 0;
    char const * errstr = strerror_r(e, buf, sizeof(buf));
    assert(errno == 0);
    throw std::runtime_error("Error while " + process + ": " + std::string(errstr));
}

class Socket {
    int s_;
public:
    Socket(int domain, int type, int protocol) :
        s_(socket(domain, type, protocol)) {
        if(s_ == -1) throw_errno("requesting socket");
    }
    void setsockopt(int level, int optname, const void *optval, socklen_t optlen) {
        int res = ::setsockopt(s_, level, optname, optval, optlen);
        if(res == -1) throw_errno("calling setsockopt");
    }
    void bind(const struct sockaddr *addr, socklen_t addrlen) {
        int res = ::bind(s_, addr, addrlen);
        if(res == -1) throw_errno("calling bind");
    }
    unsigned int recvmmsg(struct mmsghdr *msgvec, unsigned int vlen, unsigned int flags, struct timespec *timeout=nullptr) {
        int res = ::recvmmsg(s_, msgvec, vlen, flags, timeout);
        if(res == -1) throw_errno("calling recvmmsg");
        return res;
    }
};

class StereoCamera {
    Socket s_;
    uint8_t lookup[1024];
public:
    static size_t const HEIGHT = 1024;
    static size_t const WIDTH = 1280;
    StereoCamera() :
        s_(AF_INET, SOCK_DGRAM, 0) {
        int broadcast = 1; s_.setsockopt(SOL_SOCKET, SO_BROADCAST, &broadcast, sizeof broadcast);
        sockaddr_in addr;
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = htonl(INADDR_ANY);
        addr.sin_port = htons(5185);
        s_.bind((struct sockaddr *)&addr, sizeof addr);
        
        for(uint32_t i = 0; i < 1024; i++) {
          double lin = i/1023.;
          static double const a = 0.055;
          double res;
          if(lin <= 0.0031308) {
            res = 12.92 * lin;
          } else {
            res = (1+a)*pow(lin,1/2.4) - a;
          }
          res = lin;
          uint8_t res2 = std::round(255*res);
          lookup[i] = res2;
        }
    }
    void receive_frame(uint8_t *buf, uint32_t width, uint32_t height, uint32_t step) {
        static const unsigned int COUNT = 2048;
        static const unsigned int BUF_SIZE = 1028;
        mmsghdr msgvec[COUNT];
        iovec iov[COUNT];
        uint8_t bufs[COUNT][BUF_SIZE];
        for(unsigned int i = 0; i < COUNT; i++) {
            msgvec[i].msg_hdr.msg_name = nullptr;
            msgvec[i].msg_hdr.msg_namelen = 0;
            msgvec[i].msg_hdr.msg_iov = &iov[i];
            msgvec[i].msg_hdr.msg_iovlen = 1;
            msgvec[i].msg_hdr.msg_control = nullptr;
            msgvec[i].msg_hdr.msg_controllen = 0;
            msgvec[i].msg_hdr.msg_flags = 0;
            
            iov[i].iov_base = bufs[i];
            iov[i].iov_len = BUF_SIZE;
        }
        unsigned int count = s_.recvmmsg(msgvec, COUNT, MSG_TRUNC);
        for(unsigned int i = 0; i < count; i++) {
          uint32_t pos = read_be_uint32(bufs[i]+0);
          if(pos >= 2048) {
            std::cout << "invalid pos" << std::endl;
            continue;
          }
          if(msgvec[i].msg_len != 1028) {
            std::cout << "invalid size" << std::endl;
            continue;
          }
          if(pos % 2 == 0) {
            for(uint32_t j = 0; j < 256; j++) {
              uint32_t x = read_be_uint32(bufs[i]+4+4*j);
              uint32_t p1 = (x >>  0) & 1023;
              uint32_t p2 = (x >> 10) & 1023;
              uint32_t p3 = (x >> 20) & 1023;
              buf[pos/2*step + 3*j + 0] = lookup[p1];
              buf[pos/2*step + 3*j + 1] = lookup[p2];
              buf[pos/2*step + 3*j + 2] = lookup[p3];
            }
          }
          if(pos % 2 == 1) {
            for(uint32_t j = 0; j < 171; j++) {
              uint32_t x = read_be_uint32(bufs[i]+4+4*j);
              uint32_t p1 = (x >>  0) & 1023;
              uint32_t p2 = (x >> 10) & 1023;
              uint32_t p3 = (x >> 20) & 1023;
              buf[pos/2*step + 3*(j+256) + 0] = lookup[p1];
              buf[pos/2*step + 3*(j+256) + 1] = lookup[p2];
              if(j == 170) continue;
              buf[pos/2*step + 3*(j+256) + 2] = lookup[p3];
            }
          }
        //    std::cout << i << " " << msgvec[i].msg_len << " " << read_be_uint32(bufs[i]+0)-i << " " << read_be_uint32(bufs[i]+0) << std::endl;
        }
    }
};

class NodeImpl {
  boost::function<const std::string&()> getName_;
  ros::NodeHandle & nh_;
  ros::NodeHandle & private_nh_;
  ros::Publisher image_pub_;
  ros::Publisher info_pub_;
  boost::thread thinker_thread_;
  volatile bool run_;
  camera_info_manager::CameraInfoManager cinfo_;
  std::string frame_id_;
  StereoCamera sc_;
public:
  NodeImpl(boost::function<const std::string&()> getName,
  ros::NodeHandle * nhp,
  ros::NodeHandle * private_nhp) :
    getName_(getName),
    nh_(*nhp),
    private_nh_(*private_nhp),
    cinfo_(nh_,
      getParam<std::string>(private_nh_, "camera_name", "eth_video_camera"),
      getParam<std::string>(private_nh_, "camera_info_url", "")),
    frame_id_(getParam<std::string>(private_nh_, "frame_id")) {
    
    image_pub_ = nh_.advertise<sensor_msgs::Image>("image_raw", 10);
    info_pub_ = nh_.advertise<sensor_msgs::CameraInfo>("camera_info", 10);
    run_ = true;
    thinker_thread_ = boost::thread([this]() {
      while(run_) {
        boost::shared_ptr<sensor_msgs::CameraInfo> info_msg =
          boost::make_shared<sensor_msgs::CameraInfo>(cinfo_.getCameraInfo());
        boost::shared_ptr<sensor_msgs::Image> image_msgp =
          boost::make_shared<sensor_msgs::Image>();
        
        image_msgp->header.frame_id = frame_id_;
        info_msg->header = image_msgp->header;
        
        image_msgp->height = StereoCamera::HEIGHT;
        image_msgp->width = StereoCamera::WIDTH;
        image_msgp->encoding = sensor_msgs::image_encodings::BAYER_RGGB8;
        image_msgp->is_bigendian = false;
        image_msgp->step = StereoCamera::WIDTH;
        image_msgp->data.resize(image_msgp->step*StereoCamera::HEIGHT);
        
        sc_.receive_frame(image_msgp->data.data(), image_msgp->width, image_msgp->height, image_msgp->step);
        
        info_pub_.publish(info_msg);
        image_pub_.publish(image_msgp);
      }
    });
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
