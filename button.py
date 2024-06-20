from settings import *

class Button():
	def __init__(self, pos, image, text=None):
		self.rect = image.get_rect(center = pos)
		self.width = image.get_width()
		self.height = image.get_height()
		self.image = image
		self.pos = pos

		self.key = text
		self.text = text
		self.text_pos = (pos[0]+self.width/2,pos[1]+self.height/2)

		self.is_clicked = False

	def clicked(self, mouse_pos):

		if self.rect.collidepoint(mouse_pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.is_clicked == False:
				self.is_clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.is_clicked = False

		return self.is_clicked