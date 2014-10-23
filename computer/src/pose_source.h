#ifndef GUARD_QAWULBXJTLJSLKRH
#define GUARD_QAWULBXJTLJSLKRH

namespace visar {
namespace pose_source {

//base position is origin
#define BASE_POSIT 0, 0, 0
#define BASE_ANGLE 0, 0, 0
#define ACCELERATION  0.01

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
	x11::Window* window;	
	x11::Display* display;

public:
  FPSPoseSource(rendering::Renderer & r) {
		position 		<< BASE_POSIT;	//init position
		orientation << BASE_ANGLE;	//init angle
		momentum << 0, 0, 0; 				//not moving
		
		window  = r.getWindow();	//get the glx window
		display = r.getDisplay();	//get the display
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
		if(!window){	//make sure window exists
			//should probably alert somebody
			return;	//can't do anything useful, exit
		}
		
		//start listening for things
		window->SelectInput(
			PointerMotionMask |
			KeyPressMask |
			KeyReleaseMask
		);

		//Axis are handled internally as follows:
		//X-value is horizontal axis (left/right)
		//Y-value is vertical axis (up/down)
		//Z-value is depth axis (in/out)

		XEvent event;	//variable to store the event
		bool done = false;		//catch escape key
		bool update = false;	//if a key was read, update momentum
		unsigned int keycode = 0;	//storage for the keycode
		Eigen::Matrix<double, 3, 1> m2; //temporary storage, for updates
		m2 << 0, 0, 0;	//new momentum is 0 unless directed otherwise
		while(display->NextEvent(event) && !done){	//try to get event
			switch(event.type){	//switch based on type
				case MotionNotify: //Mouse is moved, adjust 
					//adjust orientation about x axis (x-axial motion)
					// or y axis (y-axial motion), if outside of neutral center
					// scroll relative to mouse distance from center
					//TODO: map relative to window direction, scroll if not center
					if(abs(event.xmotion.x) > 50){	//check if in center
						orientation[0] += (abs(event.xmotion.x) > 500)? \
							event.xmotion.x/500.0 : 1.0;	//~6-60 deg/sec
						//fix angle ranges (might not be needed)
						if (orientation[0] > 2*M_PI) orientation[0] -= 2*M_PI;
						if (orientation[0] < 0) orientation[0] += 2*M_PI;
					}
					//if moving vertically, bound at upper and lower poles
					if(event.xmotion.y > 50)	//check if moving upwards
						orientation[1] = std::min(M_PI, orientation[1] + \
							(event.xmotion.y > 500)? \
							event.xmotion.y/500.0 : 1.0);	//~6-60 deg/sec
				  else if(event.xmotion.y < -50)	//check if moving upwards
						orientation[1] = std::max(M_PI, orientation[1] + \
							(event.xmotion.y < -500.0)? \
							event.xmotion.y/500.0 : 1.0);	//~6-60 deg/sec
					printf("Caputred Motion Event: (%d, %d)\n", \
						event.xmotion.x, event.xmotion.y);	//DEBUG
					break;
					
				case KeyPress: //up/down/left/right button press
					//move forward/backwards/left/right along current axis (100 m)
					keycode = ::XLookupKeysym(&event.xkey,0);
					if(keycode == XK_Escape){
						done=true; 
						break;
					}else if (keycode == XK_Up)  m2[2] =  ACCELERATION;	//moving forward
					else if (keycode == XK_Down) m2[2] = -ACCELERATION;	//moving backward
					else if (keycode == XK_Left) m2[0] = -ACCELERATION;	//moving left
					else if (keycode == XK_Right) m2[0] = ACCELERATION;	//moving right
					printf("Caputred Key Event: code=%d\n",keycode);	//DEBUG
					
				case KeyRelease:	//key released, stop motion
					update = true;	//on either key action force update
			}
			//do something with escape key (Done)?
		}
		
		if(update) momentum = m2;	//TODO: check memory here
		
		//update the position based on current momentum
		Eigen::AngleAxisd roll(orientation[0], Eigen::Vector3d::UnitX());					
		Eigen::AngleAxisd pitch(orientation[1], Eigen::Vector3d::UnitY());					
		//Eigen::AngleAxisd yaw(orientation[2], Eigen::Vector3d::UnitZ());						
		Eigen::Quaternion<double> q = roll * pitch;
		position = position + q.matrix() * momentum;	//get the momentum
	}

	void set_pose(Eigen::Affine3d pose){
		//TODO: decompose the Affine
	}
};

}
}

#endif
