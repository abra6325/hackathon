import pynamics as pn

ctx = pn.GameManager(dimensions=pn.Dimension(500, 500), tps=64)
view = pn.ProjectWindow(ctx, size=pn.Dim(500, 500), title="Basis", color="black", scale=1)

windowtexture = pn.ImageTexture(path="texture.png", crop_resize=False, crop=(1301, 1595, 1301 + 12, 1595 + 24))
test = pn.Image(ctx, texture=windowtexture)


ctx.start()