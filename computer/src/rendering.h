#ifndef GUARD_WDZYFGEAFUDVYFMO
#define GUARD_WDZYFGEAFUDVYFMO

#include <chrono>

#include <boost/foreach.hpp>
#include <boost/optional.hpp>

#include <SDL2/SDL.h>

#include <oglplus/gl.hpp>
#include <oglplus/all.hpp>

#include <Eigen/Geometry>

namespace visar {
namespace rendering {

class IModule {
public:
  virtual ~IModule() { };
  virtual void draw() = 0;
};

class Renderer {
  boost::asio::deadline_timer timer_;
  SDL_Window * window_;
  SDL_GLContext sdlglcontext_;
  oglplus::Context gl_;
  std::vector<boost::shared_ptr<IModule> > modules_;
public:
  Renderer(boost::asio::io_service & io) :
    timer_(io) {

    if(SDL_Init(SDL_INIT_EVENTS|SDL_INIT_VIDEO) != 0)
      throw std::runtime_error(SDL_GetError());

    window_ = SDL_CreateWindow("visAR",
      SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED,
      800, 600, SDL_WINDOW_OPENGL);
    if(!window_) {
      std::runtime_error e(SDL_GetError());
      SDL_Quit();
      throw e;
    }
    
    sdlglcontext_ = SDL_GL_CreateContext(window_);

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
    gl_.Disable(oglplus::Capability::DepthTest);

    gl_.Clear().ColorBuffer();

    BOOST_FOREACH(boost::shared_ptr<IModule> & modp, modules_) {
      modp->draw();
    }

    SDL_GL_SwapWindow(window_);
  }
};


}
}

#endif
