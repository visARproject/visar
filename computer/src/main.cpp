#include <boost/asio.hpp>
#include <boost/program_options.hpp>
#include <boost/make_shared.hpp>

#include "rendering.h"
#include "simulated_world.h"
#include "pose_source.h"
#include "menu_button.h"

using namespace visar;


int main(int argc, char* argv[]) {
  namespace po = boost::program_options;
  
  po::options_description options("Allowed options"); options.add_options()
    ("help", "produce help message")
    ("pose-source", po::value<std::string>()->value_name("HOST:PORT"),
      "read pose data from HOST:PORT (default: use simulated FPS interface)")
    ("simulate-cameras", "draw simulated world instead of only overlay")
  ;
  
  po::variables_map vm;
  po::store(po::parse_command_line(argc, argv, options), vm);
  po::notify(vm);
  
  if(vm.count("help")) {
    std::cout << options;
    return EXIT_FAILURE;
  }
  
  boost::asio::io_service io;
  boost::asio::io_service::work work(io);
  
  rendering::Renderer renderer(io); // also handles window user input
  
  boost::shared_ptr<pose_source::IPoseSource> ps =
    vm.count("pose-source") ?
      boost::static_pointer_cast<pose_source::IPoseSource>(
        boost::make_shared<pose_source::RemotePoseSource>(io,
          vm["pose-source"].as<std::string>())) :
      boost::static_pointer_cast<pose_source::IPoseSource>(
        boost::make_shared<pose_source::FPSPoseSource>(renderer));
  
  if(vm.count("simulate-cameras")) {
    renderer.add_module(
      boost::make_shared<simulated_world::SimulatedWorld>(*ps));
      
    /* Adds menu buttons */
    /* First param: file name */
    /* Second param: # of buttons */
    /* Third param: location of button, 0 in middle */

    std::vector<std::string> buttons = {
      "Call_Button.png",
      "Options_Button.png",
      "Hide_All_Button.png",
    };
    
    for(int unsigned i = 0; i < buttons.size(); i++) {
      renderer.add_module(
        boost::make_shared<menu_button::Menu_Button>(buttons[i], buttons.size(), i + 1));
    }
  }
  
  io.run();
  
  return EXIT_SUCCESS;
}
