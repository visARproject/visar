#ifndef GUARD_KMNBZDOPLLIIFUCR
#define GUARD_KMNBZDOPLLIIFUCR

#include <string>
#include <cmath>
#include <oglplus/all.hpp>
#include <oglplus/bound/texture.hpp>
#include <oglplus/gl.hpp>
#include <oglplus/images/load.hpp>
#include <oglplus/images/png.hpp>
#include <oglplus/opt/smart_enums.hpp>
#include <iostream>

namespace visar {
  namespace menu {
    class Menu : public rendering::IModule {
      private:
        oglplus::Context gl;
        oglplus::VertexShader vs;
        oglplus::FragmentShader fs;
        oglplus::Program prog;
        oglplus::VertexArray rectangle;
        oglplus::Buffer verts;
        oglplus::Buffer texcoords;
        oglplus::Texture tex;
        GLfloat rectangle_verts[8];
        GLfloat tex_verts[8] = {
            0.0f, 0.0f, /* Bottom Left */
            0.0f, 1.0f, /* Top Left */
            1.0f, 0.0f, /* Bottom Right */
            1.0f, 1.0f, /* Top Right */
        };
        
      public:
        Menu(void) { }
      
        Menu(const char *t, int num_buttons, int button_loc) {
          namespace sv = oglplus::smart_values;
          oglplus::images::Image texture = oglplus::images::PNGImage(t);
          
          float tex_width = texture.Width();
          float tex_height = texture.Height();
          
          float left_x = -0.95f;
          float right_x = left_x + 0.3f;
          
          float pro_width = std::abs(right_x - left_x);
          float pro_height = pro_width * (tex_height / tex_width);
          
          float top_y = 0.0f;
          float bottom_y = 0.0f;
          
          float gap = 0.1f;
          
          if(num_buttons % 2 != 0) {
            float mid = std::ceil((float)num_buttons / 2);
            if(button_loc < mid) {
              bottom_y = ((pro_height / 2) + gap) + (mid - button_loc - 1) * (pro_height + gap);
              top_y = bottom_y + pro_height;
            } else if(button_loc > mid) {
              top_y = -(((pro_height / 2) + gap) + (button_loc - mid - 1) * (pro_height + gap));
              bottom_y = top_y - pro_height;
            } else if(button_loc == mid) {
              top_y = (pro_height / 2);
              bottom_y = -(pro_height / 2);
            } else {
              // Should never get here
              std::cout << "Problem at BYTLK";
            }
          } else if(num_buttons % 2 == 0) {
            float mid = (float)(num_buttons / 2) + 0.5f;
            
            if((float)button_loc < mid) {
              bottom_y = (gap / 2) + (mid - 0.5f - (float)button_loc) * (pro_height + gap);
              top_y = bottom_y + pro_height;
            } else if((float)button_loc > mid) {
              top_y = -((gap / 2) + ((float)button_loc - mid - 0.5f) * (pro_height + gap));
              bottom_y = top_y - pro_height;
            } else {
              // Should never get here
              std::cout << "Problem at AAAAA";
            }
          } else {
            // Should never get here
            std::cout << "Problem at PRTOR";
          }
          
          {
            rectangle_verts[0] = left_x; /* Bottom Left X */
            rectangle_verts[1] = bottom_y ; /* Bottom Left Y */
            rectangle_verts[2] = left_x; /* Top Left X */
            rectangle_verts[3] = top_y; /* Top Left Y */
            rectangle_verts[4] = right_x; /* Bottom Right X */
            rectangle_verts[5] = bottom_y; /* Bottom Right Y */
            rectangle_verts[6] = right_x; /* Top Right X */
            rectangle_verts[7] = top_y; /* Top Right Y */
          }
          
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
          
          // shader converts float to int to preform bitwise operations,
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
            .Image2D(texture)
            .MinFilter(sv::Linear)
            .MagFilter(sv::Linear)
            .Anisotropy(2.0f)
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
