#include <iostream>

#include "LibOVR/Include/OVR.h"

int main() {
    OVR::System::Init(OVR::Log::ConfigureDefaultLog(OVR::LogMask_All));
    
    OVR::HMDInfo hmdInfo = CreateDebugHMDInfo(OVR::HmdType_DK2);
    OVR::HmdRenderInfo hmd = GenerateHmdRenderInfoFromHmdInfo(hmdInfo);
    
    OVR::StereoEye eye = OVR::StereoEye_Left;
    OVR::Recti viewport = GetFramebufferViewport(eye, hmd);
    OVR::DistortionRenderDesc distortion = CalculateDistortionRenderDesc(eye, hmd);
    for(size_t x = 0; x < 1920; x++) {
        for(size_t y = 0; y < 1080; y++) {
            OVR::Vector2f NDC = TransformScreenPixelToScreenNDC(viewport, OVR::Vector2f(x, y));
            
            OVR::Vector2f resultR, resultG, resultB;
            TransformScreenNDCToTanFovSpaceChroma(&resultR, &resultG, &resultB, distortion, NDC);
            
            std::cout << x << "," << y
                << "," << resultR.x << "," << resultR.y
                << "," << resultG.x << "," << resultG.y
                << "," << resultB.x << "," << resultB.y
                << std::endl;
            //std::cout << resultR.x << " " << resultR.y << std::endl;
            //std::cout << resultG.x << " " << resultG.y << std::endl;
            //std::cout << resultB.x << " " << resultB.y << std::endl;
        }
    }
    
    return EXIT_SUCCESS;
}
