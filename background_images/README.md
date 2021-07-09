# Background images

Process background images

## Single image pipeline

Can pass in an observation to try to run the background estimation pipeline

```bash
bash background_images/single_image_pipeline.bash 2009_03/00030810060
```

To run the single image pipeline in parallel across multiple images, you can use the GNU `parallel` command.

```bash
cat background_images/lea_background_obsids.txt | parallel bash background_images/single_image_pipeline.bash
```
