#ifndef GUARD_QAWULBXJTLJSLKRH
#define GUARD_QAWULBXJTLJSLKRH

namespace visar {
namespace pose_source {


class IPoseSource {
public:
  virtual ~IPoseSource() { }
  virtual Eigen::Affine3d get_pose() const = 0;
};

class RemotePoseSource : public IPoseSource {
public:
  RemotePoseSource(boost::asio::io_service & io, std::string const & addr) {
    assert(false);
  }
  Eigen::Affine3d get_pose() const {
    assert(false);
  }
};

class FPSPoseSource : public IPoseSource {
public:
  FPSPoseSource(rendering::Renderer const & r) {
  }
  Eigen::Affine3d get_pose() const {
    return Eigen::Affine3d::Identity();
  }
};


}
}

#endif
