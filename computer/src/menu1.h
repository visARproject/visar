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
        GLfloat rectangle_verts[8] = {
            -1.0f, -1.0f,
            -1.0f, 0.0f,
            0.0f, -1.0f,
            0.0f, 0.0f,
          };
        GLfloat tex_verts[8] = {
            0.0f, 0.0f,
            0.0f, 1.0f,
            1.0f, 0.0f,
            1.0f, 1.0f,
          };
        
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
          
          //shader converts float to int to preform bitwise operations,
          // stores alpha in last bit of colors (currently 1-bit)
          // then reutrns the float, or discards if fully transparent.
          fs.Source(" \
          #version 130\n \
          uniform sampler2D TexUnit; \
          in vec2 vertTexCoord; \
          out vec4 fragColor; \
          void main(void) { \
          	vec4 t = texture(TexUnit, vertTexCoord); \
						ivec4 int_tex = ivec4(t * 255); \
						int_tex = int_tex - (int_tex % 2); \
						if(t.a > .5) int_tex += 1; \
						if(int_tex.x % 2 == 0) discard; \
						else fragColor = vec4(int_tex) / 255f; \
          } \
          ");
          
          fs.Compile();
          
          prog.AttachShader(vs);
          prog.AttachShader(fs);
          
          prog.Link();
          prog.Use();
          
          rectangle.Bind();
                    
          verts.Bind(oglplus::Buffer::Target::Array);
          {
            oglplus::Buffer::Data(oglplus::Buffer::Target::Array, 8, rectangle_verts);
            oglplus::VertexArrayAttrib vert_attr(prog, "Position");
            vert_attr.Setup<oglplus::Vec2f>().Enable();
          }
          
          texcoords.Bind(oglplus::Buffer::Target::Array);
          {
            oglplus::Buffer::Data(oglplus::Buffer::Target::Array, 8, tex_verts);
            oglplus::VertexArrayAttrib tex_attr(prog, "TexCoord");
            tex_attr.Setup<oglplus::Vec2f>().Enable();
          }
          
          gl.Bound(sv::_2D, tex)
            .Image2D(oglplus::images::PNGImage("alpha_dice.png"))
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
          prog.Use();
          rectangle.Bind();
          gl.Disable(oglplus::Capability::DepthTest);
          gl.DrawArrays(oglplus::PrimitiveType::TriangleStrip, 0, 4);
        }
    };
  }
}

#endif
