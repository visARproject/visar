#ifndef GUARD_WDZYFGEAFUDVYFMO
#define GUARD_WDZYFGEAFUDVYFMO

#include <chrono>

#include <boost/foreach.hpp>
#include <boost/optional.hpp>

#include <oglplus/gl.hpp>
#include <oglplus/all.hpp>
#include <oglplus/glx/context.hpp>
#include <oglplus/glx/version.hpp>
#include <oglplus/glx/fb_configs.hpp>
#undef Success

#include <Eigen/Geometry>

using namespace oglplus;

namespace visar {
namespace rendering {

class IModule {
public:
  virtual ~IModule() { };
  virtual void draw() = 0;
};

class Renderer {
  x11::Display display_;
  boost::asio::deadline_timer timer_;
  boost::optional<glx::FBConfig> fbc_;
  boost::optional<x11::Window> win_;
  boost::optional<glx::Context> ctx_;
  Context gl_;
  std::vector<boost::shared_ptr<IModule> > modules_;
public:
  Renderer(boost::asio::io_service & io) :
    timer_(io) {
    
    GLuint width = 800, height = 600;

    glx::Version version(display_);
    version.AssertAtLeast(1, 3);

    static int visual_attribs[] = {
      GLX_X_RENDERABLE    , True,
      GLX_DRAWABLE_TYPE   , GLX_WINDOW_BIT,
      GLX_RENDER_TYPE     , GLX_RGBA_BIT,
      GLX_X_VISUAL_TYPE   , GLX_TRUE_COLOR,
      GLX_RED_SIZE        , 8,
      GLX_GREEN_SIZE      , 8,
      GLX_BLUE_SIZE       , 8,
      GLX_ALPHA_SIZE      , 8,
      GLX_DEPTH_SIZE      , 24,
      GLX_STENCIL_SIZE    , 8,
      GLX_DOUBLEBUFFER    , True,
      None
    };
    fbc_ = glx::FBConfigs(
      display_,
      visual_attribs
    ).FindBest(display_);

    x11::VisualInfo vi(display_, *fbc_);

    win_ = boost::in_place(
      display_,
      vi,
      x11::Colormap(display_, vi),
      "visAR",
      width, height
    );

    ctx_ = boost::in_place(display_, *fbc_, 3, 0);

    ctx_->MakeCurrent(*win_);

    oglplus::GLAPIInitializer api_init;
    
    render();
  }

  void add_module(boost::shared_ptr<IModule> modulep) {
    modules_.push_back(modulep);
  }
private:
  void render() {
    timer_.expires_from_now(boost::posix_time::seconds(1./120));
    timer_.async_wait([this](boost::system::error_code const &) {
      render();
    });
    

    gl_.ClearColor(0.0f, 0.0f, 0.0f, 0.0f);
    gl_.Disable(Capability::DepthTest);
    
    gl_.Clear().ColorBuffer();
    
    BOOST_FOREACH(boost::shared_ptr<IModule> & modp, modules_) {
      modp->draw();
    }
    
    ctx_->SwapBuffers(*win_);
  }
};


}
}

#endif
