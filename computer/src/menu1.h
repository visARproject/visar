#ifndef GUARD_KMNBZDOPLLIIFUCR
#define GUARD_KMNBZDOPLLIIFUCR

#include <cmath>
#include <oglplus/all.hpp>
#include <oglplus/bound/texture.hpp>
#include <oglplus/gl.hpp>
#include <oglplus/images/load.hpp>
#include <oglplus/opt/smart_enums.hpp>

namespace visar {
  namespace menu1 {
    class Menu1 : public rendering::IModule {
      private:
        Context gl;
        VertexShader vs;
        FragmentShader fs;
        Program prog;
        VertexArray rectangle;
        Buffer verts;
        Texture tex;
      public:
        Menu1(void) { }
        void draw() {
          vs.Source(" \
            #version 130\n \
            in vec2 Position \
            void main(void) { \
              gl_Position = vec4(Position, 0.0, 1.0); \
            } \
          ");
          
          vs.Compile();
          
          fs.Source(" \
          #version 130\n \
          in vec3 vertNormal \
          out vec4 fragColor \
          void main(void) { \
            vec4 t = texture(TexUnit, vertTexCoord) \
            fragColor = vec4(1.0, 1.0, 1.0, 1.0); \
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
            1.0f, 1.0f
          };
          
          verts.Bind(Buffer::Target::Array);
          
          Buffer::Data(Buffer::Target::Array, 8, rectangle_verts);
          
          VertexArrayAttrib vert_attr(prog, "Position");
          vert_attr.Setup<Vec2f>().Enable();
          
          gl.Disable(Capability::DepthTest);
          
          gl.Bound().Image2D(images::LoadTexture("concrete_block"));
          
          gl.DrawArrays(PrimitiveType::TriangleStrip, 0, 4);
        }
    };
  }
}

#endif
