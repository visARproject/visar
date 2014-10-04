#include <oglplus/gl.hpp>
#include <oglplus/all.hpp>
#include <oglplus/glx/context.hpp>
#include <oglplus/glx/version.hpp>
#include <oglplus/glx/fb_configs.hpp>

using namespace oglplus;

int main() {
  GLuint width = 800, height = 600;

  x11::Display display;

  glx::Version version(display);
  version.AssertAtLeast(1, 3);

  static int visual_attribs[] =
  {
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
  glx::FBConfig fbc = glx::FBConfigs(
    display,
    visual_attribs
  ).FindBest(display);

  x11::VisualInfo vi(display, fbc);

  x11::Window win(
    display,
    vi,
    x11::Colormap(display, vi),
    "visAR",
    width, height
  );

  glx::Context ctx(display, fbc, 3, 3);

  ctx.MakeCurrent(win);

  oglplus::GLAPIInitializer api_init;

  // wrapper around the current OpenGL context
  Context gl;


  // Vertex shader
  VertexShader vs;
  // Set the vertex shader source
  vs.Source(" \
    #version 330\n \
    in vec3 Position; \
    void main(void) \
    { \
      gl_Position = vec4(Position, 1.0); \
    } \
  ");
  // compile it
  vs.Compile();

  // Fragment shader
  FragmentShader fs;
  // set the fragment shader source
  fs.Source(" \
    #version 330\n \
    out vec4 fragColor; \
    void main(void) \
    { \
      fragColor = vec4(1.0, 0.0, 0.0, 1.0); \
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

  GLfloat triangle_verts[9] = {
    0.0f, 0.0f, 0.0f,
    1.0f, 0.0f, 0.0f,
    0.0f, 1.0f, 0.0f
  };
  // bind the VBO for the triangle vertices
  verts.Bind(Buffer::Target::Array);
  // upload the data
  Buffer::Data(Buffer::Target::Array, 9, triangle_verts);

  // setup the vertex attribs array for the vertices
  VertexArrayAttrib vert_attr(prog, "Position");
  vert_attr.Setup<GLfloat>(3);
  vert_attr.Enable();

  gl.ClearColor(0.0f, 0.0f, 0.0f, 0.0f);
  gl.Disable(Capability::DepthTest);

  while(true) {
    gl.Clear().ColorBuffer();

    gl.DrawArrays(PrimitiveType::Triangles, 0, 3);
    ctx.SwapBuffers(win);
  }
}
