Guide to Drawables
==================

# Considerations
Why was the Visar program organized in this way?
How do I handle * weird exception?

- Drawables must be capable of handling textures (and internal framebuffers) - We'll do this by writing an overriding draw method for the drawable
- Drawables must be able to handle changes in position and orientation of both the _user_ and the _object_ (independent of eachother)
- Drawables should minimze the number of new shaders created and crazy geometries. (Handle this by creating a "Targets" drawable that draws many targets, instead of many "Target" drawables)
- Drawables should be able to be added and deleted at runtime 
- Drawables should be hideable without deletion
- There should be a single unified view matrix that moves all of the models, and each model should be able to own its own position matrix
- - Rather, there should be a capability for, but not a requirements of, a unified view matrix. That is, multiple view matrice should be possible for UI elements and world elements.

- Transparency should be allowed (Handle with alpha)
- We need to care for the limits of floating point precision, because weird things *should* happen if the user has moved too far

## Ideas for handling multiple views
- Flag in the vertex shader indicating "UI element" (i.e. don't rotate me)
- Different implementation in the shader
- Subclass from an entirely different drawable

# Guidelines
## Draw Method
- DO NOT CLEAR THE DEPTH BUFFER
- DO NOT CLEAR THE DEPTH BUFFER
- DO NOT CLEAR THE DEPTH BUFFER
- DO NOT CLEAR THE DEPTH BUFFER
- DO NOT CLEAR THE DEPTH BUFFER
- DO NOT CLEAR THE DEPTH BUFFER
(Unless you have a good reason, meaning you know what you are doing). Ex: using a framebuffer internal to the drawable

## Shader Property
- return (Vertex shader, Fragment shader)

# Pipeline
At the very beginning, we bind all of the shader programs and their associated vertex information. It is permitted to add to this at any time.

At each run through the main 'draw' function, we iterate through the drawables, and draw them,
We then move the view (by changing the view matrix) exactly the inter-pupilary distance (IPD, not related to IPPD), and draw it again to simulate having both eye views.



## Notes
When you are using a single program to draw multiple objects, generate a vertex buffer for each object and bind them one at a time. Delete your vertex buffers when you're done with them!

In fact, anything that you're done with you should delete!
