import numpy as np
from vispy.geometry import create_cube
from vispy.util.transforms import perspective, translate, rotate
from vispy.gloo import (Program, VertexBuffer, IndexBuffer, Texture2D, clear,
                        FrameBuffer)

from ..rift_parameters import read_mesh_txt
'''Example vert_shader

float2 EyeToSourceUVScale, EyeToSourceUVOffset;
float4x4 EyeRotationStart, EyeRotationEnd;
float2 TimewarpTexCoord(float2 TexCoord, float4x4 rotMat)
{
// Vertex inputs are in TanEyeAngle space for the R,G,B channels (i.e. after chromatic
// aberration and distortion). These are now "real world" vectors in direction (x,y,1)
// relative to the eye of the HMD. Apply the 3x3 timewarp rotation to these vectors.
float3 transformed = float3( mul ( rotMat, float4(TexCoord.xy, 1, 1) ).xyz);
// Project them back onto the Z=1 plane of the rendered images.
float2 flattened = (transformed.xy / transformed.z);
// Scale them into ([0,0.5],[0,1]) or ([0.5,0],[0,1]) UV lookup space (depending on eye)
return(EyeToSourceUVScale * flattened + EyeToSourceUVOffset);
}
void main(in float2 Position : POSITION, in float timewarpLerpFactor : POSITION1,
in float Vignette : POSITION2, in float2 TexCoord0 : TEXCOORD0,
in float2 TexCoord1 : TEXCOORD1, in float2 TexCoord2 : TEXCOORD2,
out float4 oPosition : SV_Position, out float2 oTexCoord0 : TEXCOORD0,
out float2 oTexCoord1 : TEXCOORD1, out float2 oTexCoord2 : TEXCOORD2,
out float oVignette : TEXCOORD3)
{
float4x4 lerpedEyeRot = lerp(EyeRotationStart, EyeRotationEnd, timewarpLerpFactor);
oTexCoord0 = TimewarpTexCoord(TexCoord0,lerpedEyeRot);
oTexCoord1 = TimewarpTexCoord(TexCoord1,lerpedEyeRot);
oTexCoord2 = TimewarpTexCoord(TexCoord2,lerpedEyeRot);
oPosition = float4(Position.xy, 0.5, 1.0);
o
'''

''' Example frag_shader

Texture2D Texture : register(t0);
SamplerState Linear : register(s0);
float4 main(in float4 oPosition : SV_Position, in float2 oTexCoord0 : TEXCOORD0,
in float2 oTexCoord1 : TEXCOORD1, in float2 oTexCoord2 : TEXCOORD2,
in float oVignette : TEXCOORD3) : SV_Target
{
// 3 samples for fixing chromatic aberrations
float R = Texture.Sample(Linear, oTexCoord0.xy).r;
float G = Texture.Sample(Linear, oTexCoord1.xy).g;
float B = Texture.Sample(Linear, oTexCoord2.xy).b;
return (oVignette*float4(R,G,B,1));
}
'''

class Mesh(object):
    ''' Expect
        ('pos', np.float32, 2),
        ('red_xy', np.float32, 2),
        ('green_xy', np.float32, 2),
        ('blue_xy', np.float32, 2),
        ('vignette', np.float32, 1),
    '''
    _i_buffers, _v_buffers = read_mesh_txt.read()

    _vert_shader = '''
    #version 120
    attribute vec2 pos;
    attribute vec2 red_xy;
    attribute vec2 green_xy;
    attribute vec2 blue_xy;
    attribute float vignette;
    
    varying vec2 oRed_xy;
    varying vec2 oGreen_xy;
    varying vec2 oBlue_xy;
    varying float oVignette;
    void main() {
        gl_Position = vec4(pos.xy, 0.5, 1.0);
        oRed_xy = red_xy;
        oRed_xy.y = 1 - oRed_xy.y;
        oGreen_xy = green_xy;
        oGreen_xy.y = 1 - oGreen_xy.y;
        oBlue_xy = blue_xy;
        oBlue_xy.y = 1 - oBlue_xy.y;
        
        oRed_xy = vec2(oRed_xy.x + 1.2, oRed_xy.y + 0.13);
        oGreen_xy = vec2(oGreen_xy.x + 1.2, oGreen_xy.y + 0.13);
        oBlue_xy = vec2(oBlue_xy.x + 1.2, oBlue_xy.y + 0.13);

        // oRed_xy = vec2(oRed_xy.x + 1.2, oRed_xy.y + 0.13);
        // oGreen_xy = vec2(oGreen_xy.x + 1.2, oGreen_xy.y + 0.13);

        oVignette = vignette;

        // oRed_xy = red_xy;
        // oRed_xy.y = 1.0 - oRed_xy.y;
        // oGreen_xy = green_xy;
        // oGreen_xy.y = 1.0 - oGreen_xy.y;
        // oBlue_xy = blue_xy;
        // oBlue_xy.y = 1.0 - oBlue_xy.y;

    }
    '''

    _frag_shader = '''
    #version 120
    // -> Add capability for setting "enable-aberration, disable rift-projection"
    uniform sampler2D texture;
    varying vec2 oRed_xy;
    varying vec2 oGreen_xy;
    varying vec2 oBlue_xy;
    varying float oVignette;

    void main() {

        int test = 0;
        float tex_scale = 0.1;

        float r = texture2D(texture, (oRed_xy * tex_scale)).r;
        float g = texture2D(texture, (oGreen_xy * tex_scale)).g;
        float b = texture2D(texture, (oBlue_xy * tex_scale)).b;
        if (test == 1) {

            r = 0.0;
            g = 0.0;
            b = 0.0;
            if ((tex_scale * oBlue_xy.x) < 0.0) {
                b = 0.9;
            }
            if ((tex_scale * oBlue_xy.x) > 1.0) {
                b = 0.2;
            }
            if ((tex_scale * oBlue_xy.y) > 1.0) {
                r = 0.9;
            }
            if ((tex_scale * oBlue_xy.y) < 0.0) {
                r = 0.2;
            }
        }
        gl_FragColor = vec4(r, g, b, 1);

        if (test == 2) {
            gl_FragColor = vec4(oRed_xy.x * tex_scale, oRed_xy.y * tex_scale, 1, 1);
        }

        //gl_FragColor = vec4(oGreen_xy.x * 2, oGreen_xy.y * 2, 1, 1);
        // gl_FragColor = vec4(1, 0.5, b, 1);

    }
    '''

    @classmethod
    def make_eye(self, texture, eye):
        assert isinstance(texture, Texture2D), "texture not a texture 2D instance!"
        assert eye in ['left', 'right'], eye + " is not a valid eye (Should be left or right)"

        program = Program(self._vert_shader, self._frag_shader)
        # v_buffer = VertexBuffer(self._v_buffers['left_buffer'])

        i_buffer = self._i_buffers[eye + '_indices']
        _buffer = self._v_buffers[eye + '_buffer']

        print 'Loading pos -> GPU memory'
        program['pos'] = _buffer['pos']
        print 'Loading red_xy -> GPU memory'
        program['red_xy'] = _buffer['red_xy']
        print 'Loading green_xy -> GPU memory'
        program['green_xy'] = _buffer['green_xy']
        print 'Loading blue_xy -> GPU memory'
        program['blue_xy'] = _buffer['blue_xy']
        program['vignette'] = _buffer['vignette']
        program['texture'] = texture

        print _buffer['vignette']

        return program, IndexBuffer(i_buffer)

    @classmethod
    def make_right_eye(self, texture):
        return NotImplemented
