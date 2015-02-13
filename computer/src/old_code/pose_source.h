#ifndef GUARD_QAWULBXJTLJSLKRH
#define GUARD_QAWULBXJTLJSLKRH

namespace visar {
namespace pose_source {

//base position is origin
#define BASE_POSIT 0, 0, 0
#define BASE_ANGLE 0, 0, 0
#define LIN_VELOCITY  0.01
#define ANG_VELOCITY  0.01

class IPoseSource {
public:
  virtual ~IPoseSource() { }
  virtual Eigen::Affine3d get_pose() = 0;
};

class RemotePoseSource : public IPoseSource {
public:
  RemotePoseSource(boost::asio::io_service & io, std::string const & addr) {
    assert(false);
  }
  Eigen::Affine3d get_pose() {
    assert(false);
  }
};

class FPSPoseSource : public IPoseSource {
	Eigen::Matrix<double, 3, 1> position;
	Eigen::Matrix<double, 3, 1> orientation;
	Eigen::Matrix<double, 3, 1> momentum; //cache directional data
	Eigen::Matrix<double, 3, 1> rotation; //cache angular data
	int window_size[2];

public:
  FPSPoseSource(rendering::Renderer & r) {
		position 		<< BASE_POSIT;	//init position
		orientation << BASE_ANGLE;	//init angle
		momentum << 0, 0, 0; 				//not moving
		
		//get the display size (from rendering.h)
		window_size[0] = 800;
		window_size[1] = 600;
  }

	//function will return the pose of the user, and will also
	// check for changes in user state (button presses) if vel_update
  Eigen::Affine3d get_pose() {
		vel_update_pose();	//call the vel_update
		
		//generate affine transformation from translation and 2 angles
		Eigen::Affine3d a = Eigen::Translation3d(position) * \
			Eigen::AngleAxisd(orientation[0], Eigen::Vector3d::UnitX()) * \
			Eigen::AngleAxisd(orientation[1], Eigen::Vector3d::UnitY()) * \
			Eigen::AngleAxisd(orientation[2], Eigen::Vector3d::UnitZ());
    return a;	//return the transformation
  }

	void vel_update_pose(){
		//Axis are handled internally as follows:
		//X-value is horizontal axis (left/right)
		//Y-value is vertical axis (up/down)
		//Z-value is depth axis (in/out)

		SDL_Event event;	//variable to store the event
		bool done = false;		//catch escape key
		bool vel_update = false;	//if a key was read, update momentum
		bool rot_update = false;	//if a key was read, update rotation
		SDL_Keycode keycode = 0;	//storage for the keycode
		Eigen::Matrix<double, 3, 1> m2,r2; //temporary storage, for vel_updates
		m2 << 0, 0, 0;	//new momentum is 0 unless directed otherwise
		r2 << 0, 0, 0;	//new velocity is 0 unless directed otherwise
		while(SDL_PollEvent(&event) && !done){	//try to get event
			switch(event.type){	//switch based on type
				case SDL_MOUSEMOTION: //Mouse is moved, adjust 
					//if moving horizontally, rotate around y axis
					if(event.motion.x - window_size[0]/2 > window_size[0]*.1)	//check threshold
						r2[1] = -ANG_VELOCITY;
					else if(event.motion.x - window_size[0]/2 < window_size[0]*-.1)	//check threshold
						r2[1] = ANG_VELOCITY;
					
					//if moving vertically, bound at upper and lower poles, rotate around x axis
					if(event.motion.y - window_size[1]/2 > window_size[1]*.1)	//check threshold
						r2[0] = -ANG_VELOCITY;
				  else if(event.motion.y - window_size[1]/2 < window_size[1]*-.1)	//check threshold
						r2[0] = ANG_VELOCITY;
					rot_update = true;	//there was an update
					/*printf("Caputred Motion Event: (%d, %d)\n", \
						event.xmotion.x, event.xmotion.y);	//DEBUG*/
					break;
					
				case SDL_KEYDOWN: //up/down/left/right button press
					//move forward/backwards/left/right along current axis (100 m)
					keycode = event.key.keysym.sym;
					if(keycode == SDLK_ESCAPE){
						done=true; 
						break;
					}else if (keycode == SDLK_UP)  m2[2] =  LIN_VELOCITY;	//moving forward
					else if (keycode == SDLK_DOWN) m2[2] = -LIN_VELOCITY;	//moving backward
					else if (keycode == SDLK_LEFT) m2[0] = -LIN_VELOCITY;	//moving left
					else if (keycode == SDLK_RIGHT) m2[0] = LIN_VELOCITY;	//moving right
					//else if (keycode == SDLK_ESCAPE) throw;	//TODO: make this work
					//printf("Caputred Key Event: code=%d\n",keycode);	//DEBUG
					
				case SDL_KEYUP:	//key released, stop motion
					vel_update = true;	//on either key action force vel_update
					break;
					
				case SDL_QUIT:
					throw;	//throw exception to force exit
			 
			}
			//do something with escape key (Done)?
		}
		
		if(vel_update) momentum = m2;	//TODO: check memory here
		if(rot_update) rotation = r2;	
		orientation = orientation + rotation;
		
		//bound the x-orientatino to the poles
		if(orientation[0] > M_PI*.5) orientation[0] = M_PI*.5;
		if(orientation[0] < -M_PI*.5) orientation[0] = -M_PI*.5;
		//wrap the y-orientaiton in [0,2*PI]
		if(orientation[1] < 0) orientation[1] += M_PI;
		if(orientation[1] > 2*M_PI) orientation[1] -= M_PI;
		
		//vel_update the position based on current momentum
		Eigen::AngleAxisd roll(orientation[0], Eigen::Vector3d::UnitX());					
		Eigen::AngleAxisd pitch(orientation[1], Eigen::Vector3d::UnitY());					
		Eigen::AngleAxisd yaw(orientation[2], Eigen::Vector3d::UnitZ());						
		Eigen::Quaternion<double> q = roll * pitch * yaw;
		position = position + q.matrix() * momentum;	//get the momentum
	}

	void set_pose(Eigen::Affine3d pose){
		position = pose.translation();	//get the pose translation
	}
};

}
}

#endif
