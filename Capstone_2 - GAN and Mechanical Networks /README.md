# Develop a Image-to-Image Translation Model to Capture Local Interactions in Mechanical Networks (GAN)


### Quick Summary

Metamaterials are materials whose mechanical properties rely on their structure, which grant them modes of deformation that are not found in conventional systems. Whether they're realized at the micro- or macro-scale, the model is the same: building blocks connected to one another defines the mechanical structure of the material. These are called **mechanical networks**. How the blocks are distributed in space and how they connect with one another are precisely what determine the mechanical nature of the material. The connectivity between the blocks define the class of materials: Kagome, square, triangular, etc... Those will possess different mechanical properties. Additionally, within each class of materials, how the blocks are spread out in space also determine the mechanics of the system. In other words, both position and connectivity of the blocks are critical to know.

Often enough, these materials are visually described by a lattice representation: *points* (known as nodes) representing the blocks are connected by *bonds* (also known as edges). In some instances, a user will only be given the distribution of the points, but will miss on the bond connectivity. **This model is intended to use deep learning and neural networks to automatically draw the bond connections on images that contain the points solely.**

To achieve our goal, we follow Jason Brownless' article for Machine Learning Mastery on how to develop a **GAN (Generative Adversarial Network)** from scratch. The notebook used is a Google's Colab Notebook, which allowed me to access Google's GPU services to build and train the model. By training on 100s images of different mechanical networks (with and without bonds connectivity drawn) only, the model I built is able to plot the bond connectivity automatically on systems it has never seen before. While the result itself is pretty astonishing, the **architecture of the model**, which relies on **Convulational Neural Networks**, **Discriminating** and **Generating algorithms** is equally important to understand.

I recommend to check out the notebook found in this directory, along with the final report and the slides to learn more about this project.
