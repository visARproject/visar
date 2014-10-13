#ifndef GUARD_WDZYFGEAFUDVYFMO
#define GUARD_WDZYFGEAFUDVYFMO

#include <chrono>

#include <boost/optional.hpp>

#include <oglplus/gl.hpp>
#include <oglplus/all.hpp>
#include <oglplus/glx/context.hpp>
#include <oglplus/glx/version.hpp>
#include <oglplus/glx/fb_configs.hpp>

using namespace oglplus;

namespace visar {
namespace rendering {


class Renderer {
  x11::Display display_;
  boost::asio::deadline_timer timer_;
  boost::optional<glx::FBConfig> fbc_;
  boost::optional<x11::Window> win_;
  boost::optional<glx::Context> ctx_;
  Context gl_;
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

private:
  void render() {
    timer_.expires_from_now(boost::posix_time::seconds(1./120));
    timer_.async_wait([this](boost::system::error_code const &) { render(); });
    
    // Vertex shader
    VertexShader vs;
    // Set the vertex shader source
    vs.Source(" \
      #version 130\n \
      in vec3 Position; \
      varying vec3 verpos; \
      void main(void) \
      { \
        gl_Position = vec4(Position, 1.0); \
        verpos = Position; \
      } \
    ");
    // compile it
    vs.Compile();

    // Fragment shader
    FragmentShader fs;
    // set the fragment shader source
    fs.Source(" \
      #version 130\n \
      out vec4 fragColor; \
      varying vec3 verpos; \
      void main(void) \
      { \
        float a = sin(101*(verpos.x+verpos.y+verpos.z))/2+.5; \
        fragColor = vec4(a, a, a, 1.0); \
      } \
    ");
    // compile it
    fs.Compile();

    // Program
    Program prog;
    // attach the shaders to the program
    prog.AttachShader(vs);
    prog.AttachShader(fs);
    // link and use it
    prog.Link();
    prog.Use();


    // A vertex array object for the rendered triangle
    VertexArray triangle;
    // VBO for the triangle's vertices
    Buffer verts;

    // bind the VAO for the triangle
    triangle.Bind();

    // bind the VBO for the triangle vertices
    verts.Bind(Buffer::Target::Array);

    // setup the vertex attribs array for the vertices
    VertexArrayAttrib vert_attr(prog, "Position");
    vert_attr.Setup<GLfloat>(3);
    vert_attr.Enable();

    gl_.ClearColor(0.0f, 0.0f, 0.0f, 0.0f);
    gl_.Disable(Capability::DepthTest);
    
    gl_.Clear().ColorBuffer();

    auto some_time = std::chrono::high_resolution_clock::now().time_since_epoch();
    double t = std::chrono::duration_cast<std::chrono::duration<double>>(some_time).count();

    double s = sin(t), c = cos(t);
    double triangle_verts[9] = {
      0, .5 , 0,
      .5*s*sqrt(3)/2, .5*-.5, .5*c*sqrt(3)/2,
      .5*-s*sqrt(3)/2, .5*-.5, .5*-c*sqrt(3)/2,
    };
    GLfloat triangle_verts2[9];
    for(size_t i = 0; i < 9; i++) {
      triangle_verts2[i] = triangle_verts[i];
    }
    // upload the data
    Buffer::Data(Buffer::Target::Array, 9, triangle_verts2);

    gl_.DrawArrays(PrimitiveType::Triangles, 0, 3);
    ctx_->SwapBuffers(*win_);
  }
};


}
}

#endif
