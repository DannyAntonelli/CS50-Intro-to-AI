# Traffic
Write an AI to identify which traffic sign appears in a photograph.

## How I started
My first idea was to recreate the model I saw in the lecture, so I structured mine as follows:

- **Convolutional layer**, *32 filters* using a *3x3 kernel*
- **Max-pooling layer**, using *2x2 pool size*
- **Hidden-Layer**, *8 x NUM_CATEGORIES (43)* nodes with *relu activation*
- **Dropout rate** of *0.5*

These are the result I get from this initial model: *0.6207 testing accuracy*.

I was not quite satisfied with the result so I decided to apply some minor changes to it.

## Trial and error
At first I played a little bit with the numbers, changing the convolutional layer from *32 to 48 filters*, adding additional *4 x NUM_CATEGORIES* nodes to the hidden layer and setting a dropout rate of *0.4*.

The result I got was pretty surprising to me: *0.9306 testing accuracy*.

So the problem of my initial model is that it was too simple to be used for image recognition, and a little complexity helped a lot.

So after that i tried some other changes to see if even more complexity was useful for the purpose.

A second max-pooling layer didn't to the work, because the accuracy dropped to *0.8434* so I decided to get rid of it.

Adding another hidden layer turned out to be not very promising, in fact the accuracy stayed pretty much the same as before: *0.9247*. I removed it.

So my last idea was to try to add a second convolutional layer a little different from the first. The result were good and the testing accuracy went from the initial *0.9306* to *0.9534*, not a huge leap, but a slight improvement!

## Final model
So here is the final model I designed:

- First **convolutional layer**, *48 filters* using a *3x3 kernel*
- Second **convolutional layer**, *32 filters* using a *4x4 kernel*
- **Max-pooling layer**, using *2x2 pool size*
- **Hidden-Layer**, *12 x NUM_CATEGORIES (43)* nodes with *relu activation*
- **Dropout rate** of *0.4*

**Final testing accuracy**: *0.9534*