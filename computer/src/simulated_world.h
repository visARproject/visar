#ifndef GUARD_JKMSETLTJSBVGOBX
#define GUARD_JKMSETLTJSBVGOBX

#include <oglplus/gl.hpp>

#include "pose_source.h"

namespace visar {
namespace simulated_world {

class SimulatedWorld : public rendering::IModule {
	pose_source::IPoseSource* ps;
	
public:
  SimulatedWorld(pose_source::IPoseSource & ps) { 
  	this->ps = &ps;	//store the pose
  }
  
  void draw() {
    // Vertex shader
    oglplus::VertexShader vs;
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
    oglplus::FragmentShader fs;
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
    oglplus::Program prog;
    // attach the shaders to the program
    prog.AttachShader(vs);
    prog.AttachShader(fs);
    // link and use it
    prog.Link();
    prog.Use();


    // A vertex array object for the rendered triangle
    oglplus::VertexArray triangle;
    // VBO for the triangle's vertices
    oglplus::Buffer verts;

    // bind the VAO for the triangle
    triangle.Bind();

    // bind the VBO for the triangle vertices
    verts.Bind(oglplus::Buffer::Target::Array);

    // setup the vertex attribs array for the vertices
    oglplus::VertexArrayAttrib vert_attr(prog, "Position");
    vert_attr.Setup<GLfloat>(3);
    vert_attr.Enable();

    auto some_time = std::chrono::high_resolution_clock::now().time_since_epoch();
    double t = std::chrono::duration_cast<std::chrono::duration<double>>(some_time).count();

    double s = sin(t), c = cos(t);
    double triangle_verts[9] = {
      0, .5 , 0,
      .5*s*sqrt(3)/2, .5*-.5, .5*c*sqrt(3)/2,
      .5*-s*sqrt(3)/2, .5*-.5, .5*-c*sqrt(3)/2,
    };
    
    //get the transformation
    Eigen::Affine3d pose = ps->get_pose();
    
    //transform each of the vertices and store in GLfloat triange
    GLfloat triangle_verts2[9];
    for(size_t i=0; i<3; ++i){
    	Eigen::Matrix<double, 4, 1> v;
    	v << triangle_verts[i*3], triangle_verts[i*3+1], triangle_verts[i*3+2], 1;
    	v = pose * v;	//preform the transformation
    	triangle_verts2[i*3] = v[0];	//store results
    	triangle_verts2[i*3+1] = v[1];
 	    triangle_verts2[i*3+2] = v[2];
    }
   
    // upload the data
    oglplus::Buffer::Data(oglplus::Buffer::Target::Array, 9, triangle_verts2);

    oglplus::Context::DrawArrays(oglplus::PrimitiveType::Triangles, 0, 3);
  }
};


}
}

#endif
