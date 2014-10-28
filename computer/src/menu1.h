#ifndef GUARD_KMNBZDOPLLIIFUCR
#define GUARD_KMNBZDOPLLIIFUCR

#include <cmath>
#include <oglplus/all.hpp>
#include <oglplus/bound/texture.hpp>
#include <oglplus/gl.hpp>
#include <oglplus/images/load.hpp>
#include <oglplus/images/png.hpp>
#include <oglplus/opt/smart_enums.hpp>

namespace visar {
  namespace menu1 {
    class Menu1 : public rendering::IModule {
      private:
        oglplus::Context gl;
        oglplus::VertexShader vs;
        oglplus::FragmentShader fs;
        oglplus::Program prog;
        oglplus::VertexArray rectangle;
        oglplus::Buffer verts;
        oglplus::Buffer texcoords;
        oglplus::Texture tex;
      public:
        Menu1(void) {
          namespace sv = oglplus::smart_values;
          vs.Source(" \
            #version 130\n \
            in vec2 Position; \
            in vec2 TexCoord; \
            out vec2 vertTexCoord; \
            void main(void) { \
              gl_Position = vec4(Position, 0.0, 1.0); \
              vertTexCoord = TexCoord; \
            } \
          ");
          
          vs.Compile();
          
          fs.Source(" \
          #version 130\n \
          uniform sampler2D TexUnit; \
          in vec2 vertTexCoord; \
          out vec4 fragColor; \
          void main(void) { \
            vec4 t = texture(TexUnit, vertTexCoord); \
            fragColor = vec4(t.x, t.y, t.z, 1f); \
          } \
          ");
          
          fs.Compile();
          
          prog.AttachShader(vs);
          prog.AttachShader(fs);
          
          prog.Link();
          prog.Use();
          
          rectangle.Bind();
          
          GLfloat rectangle_verts[8] = {
            -1.0f, -1.0f,
            -1.0f, 1.0f,
            1.0f, -1.0f,
            1.0f, 1.0f,
          };
          
          verts.Bind(oglplus::Buffer::Target::Array);
          {
            oglplus::Buffer::Data(oglplus::Buffer::Target::Array, 8, rectangle_verts);
            oglplus::VertexArrayAttrib vert_attr(prog, "Position");
            vert_attr.Setup<oglplus::Vec2f>().Enable();
          }
          
          GLfloat tex_verts[8] = {
            0.0f, 0.0f,
            0.0f, 1.0f,
            1.0f, 0.0f,
            1.0f, 1.0f,
          };
          
          texcoords.Bind(oglplus::Buffer::Target::Array);
          {
            oglplus::Buffer::Data(oglplus::Buffer::Target::Array, 8, tex_verts);
            oglplus::VertexArrayAttrib tex_attr(prog, "TexCoord");
            tex_attr.Setup<oglplus::Vec2f>().Enable();
          }
          
          gl.Bound(sv::_2D, tex)
            .Image2D(oglplus::images::PNGImage("concrete_block.png"))
            .MinFilter(sv::Linear)
            .MagFilter(sv::Linear)
            .Anisotropy(2.0f)
            .WrapS(sv::ClampToEdge)
            .WrapT(sv::ClampToEdge)
            .WrapR(sv::ClampToEdge)
            .GenerateMipmap();
          
          (prog/"TexUnit") = 0;
        }
        void draw() {
          gl.Disable(oglplus::Capability::DepthTest);
          gl.DrawArrays(oglplus::PrimitiveType::TriangleStrip, 0, 4);
        }
    };
  }
}

#endif
