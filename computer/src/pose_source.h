#ifndef GUARD_QAWULBXJTLJSLKRH
#define GUARD_QAWULBXJTLJSLKRH

namespace visar {
namespace pose_source {

//deifne mil's position as a constant
#define BASE_POSIT 0
#define BASE_ANGLE 0

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
	Eigen::Matrix<double, 3, 1> momentum;
	boost::optional<x11::Window>* window;	//what's going on here? I don't know
	x11::Display* display;

public:
  FPSPoseSource(rendering::Renderer const & r) {
		momentum << 0, 0, 0;	//not moving
		//talk to forrest about making these avaliable somehow
		window = &(r.win_);
		display = &(r.display_);
  }

	//function will return the pose of the user, and will also
	// check for changes in user state (button presses) if update
  Eigen::Affine3d get_pose() {
		update_pose();	//call the update
		
		//generate affine transformation from translation and 2 angles
		Eigen::Affine3d a = Eigen::Translation3d(position) * \
			Eigen::AngleAxisd(orientation[1], Eigen::Vector3d::UnitY()) * \
			Eigen::AngleAxisd(orientation[2], Eigen::Vector3d::UnitZ());
    return a;	//return the transformation
  }

	void update_pose(){
		//start listening for things
		window->SelectInput(
			PointerMotionMask|
			KeyPressMask
		);

		XEvent event;	//variable to store the event
		bool done = false;
		while(display->NextEvent(event) && !done){	//try to get event
			switch(event.type){	//switch based on type
				case MotionNotify: //Mouse is moved, adjust 
					//adjust orientation about z axis (x-axial motion)
					// or y axis (y-axial motion), if outside of neutral center
					// scroll relative to mouse distance from center
					if(abs(event.xmotion.x_root) > 50){	//check if in center
						orientation[2] += (abs(event.xmotion.x_root) > 500)? \
							event.xmotion.x_root/500.0 : 1.0;	//~6-60 deg/sec
						//fix angle ranges (might not be needed)
						if (orientation[2] > 2*M_PI) orientation[2] -= 2*M_PI;
						if (orientation[2] < 0) orientation[2] += 2*M_PI;
					}
					//if moving vertically, bound at upper and lower poles
					if(event.xmotion.y_root > 50)	//check if moving upwards
						orientation[1] = std::min(M_PI, orientation[1] + \
							(event.xmotion.y_root > 500)? \
							event.xmotion.y_root/500.0 : 1.0);	//~6-60 deg/sec
				  else if(event.xmotion.y_root < -50)	//check if moving upwards
						orientation[1] = std::max(M_PI, orientation[1] + \
							(event.xmotion.y_root < -500.0)? \
							event.xmotion.y_root/500.0 : 1.0);	//~6-60 deg/sec
					break;
					
				case KeyPress: //up/down/left/right button press
					//move forward/backwards/left/right along current axis (100 m)
					unsigned int keycode = ::XLookupKeysym(&event.xkey,0);
					int type = (event.xkey.type);	//0 = pressed?
					if(keycode == XK_Escape){
						done=true; 
						break;
					} else if ((keycode == XK_Up && type) || \
						(keycode == XK_Down && !type))	momentum[0] += 100;	//moving forward
					else if ((keycode == XK_Up && !type) || \
						(keycode == XK_Down && type))	momentum[0] -= 100;	//moving backward
					else if ((keycode == XK_Left && type) || \
						(keycode == XK_Right && !type))	momentum[1] -= 100;	//moving left
					else if ((keycode == XK_Left && !type) || \
						(keycode == XK_Right && type))	momentum[1] += 100;	//moving right
			}
			//do something with done value?
			
			//update the position based on current momentum
			Eigen::AngleAxisd pitch(orientation[1], Eigen::Vector3d::UnitY());					
			Eigen::AngleAxisd yaw(orientation[2], Eigen::Vector3d::UnitX());						
			Eigen::Quaternion<double> q = pitch * yaw;
			position = position + q.matrix() * momentum;	//get the momentum
		}
	}

	void set_pose(Eigen::Affine3d pose){
		//set some position thing
		
	}
};

}
}

#endif
