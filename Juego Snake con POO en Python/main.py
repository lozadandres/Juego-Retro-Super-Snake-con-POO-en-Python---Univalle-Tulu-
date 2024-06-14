import pygame
import random
#El juego es en dos dimensiones (2D) por sus representación y mecánicas

# Inicializar Pygame
pygame.init()

# Definición de constantes
WIDTH, HEIGHT = 800, 600 # Ancho y alto de la pantalla del juego
CELL_SIZE = 20 # Tamaño de cada celda en la cuadrícula del juego
# Color en formato RGB
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (255, 0, 255)
CAFEOS = (75, 54, 33)
CAFE = (139, 69, 19)
FPS = 10 # Fotogramas por segundo, determina la velocidad del juego

# Configuración de la pantalla
screen = pygame.display.set_mode((WIDTH, HEIGHT)) # Creación de la ventana del juego con el tamaño especificado
pygame.display.set_caption('Retro Super Snake')
# Cargar el icono
icon = pygame.image.load('assets/imagenes/Snake-icon.png')
# Establecer el icono
pygame.display.set_icon(icon)

# Fuente para el puntaje
font = pygame.font.Font(None, 36)

# Función para cargar y escalar imágenes
def load_and_scale_image(filename, size):
    image = pygame.image.load(filename) # Carga la imagen
    return pygame.transform.scale(image, size) # Escala la imagen al tamaño deseado

# Clase base para todos los elementos del juego
class GameObject: #Utiliza la palabra clave class seguida del nombre de la clase para definir una clase, en este caso es una clase abstracta
    def __init__(self, position):
        self.position = position # Atributo que almacena la posición del objeto. No es abstracto en sí mismo, pero las clases hijas deben implementarlo

    def draw(self, screen): #No es abstracto en sí mismo, pero se espera que las clases hijas lo implementen, gracias a el tambien se hace polimorfismo ya que su implementación difiere según la clase. Esto permite que el método draw se comporte de manera diferente según el tipo de objeto que se está dibujando.
        pass

# Clase para la comida
class Food(GameObject): #Para la herencia, simplemente coloca el nombre de la clase padre entre paréntesis al definir la clase hija.
    def __init__(self, position):
        super().__init__(position) #llama al medodo posiccion dela clase padre o base (GameObject) para inicializar la posición de la comida
        self.image = load_and_scale_image('assets/imagenes/Red-Apple-icon.png', (25, 25)) # Carga y escala la imagen

    def draw(self, screen):
        screen.blit(self.image, self.position) # Dibuja la imagen de la comida en la posición actual en la pantalla

# Clase para la serpiente
class Snake(GameObject): # la clase Snake implementa el encapsulamiento ya que los atributos directions, body, direction, growing, y speed_boost son internos a la clase y no son accesibles directamente desde fuera de la clase. Los métodos move, grow, y draw proporcionan formas controladas de interactuar con estos atributos.
    def __init__(self, position):
        super().__init__(position)  #llama al medodo posiccion dela clase padre o base (GameObject) para inicializar la posición de la serpiente
        # Diccionario que mapea nombres de direcciones a vectores de movimiento
        self.directions = {
            'UP': pygame.Vector2(0, -1),
            'DOWN': pygame.Vector2(0, 1),
            'LEFT': pygame.Vector2(-1, 0),
            'RIGHT': pygame.Vector2(1, 0)
        }
        # Lista que almacena las posiciones de cada segmento del cuerpo de la serpiente
        self.body = [position, position - pygame.Vector2(CELL_SIZE, 0)] # La serpiente inicia con dos segmentos
        self.direction = pygame.Vector2(1, 0) # Dirección inicial de la serpiente
        self.growing = False # Indica si la serpiente está creciendo
        self.speed_boost = False # Indica si la serpiente está en modo de aumento de velocidad
        self.eye_offset = [(7, 7), (CELL_SIZE - 7 * 2, 7)] # Posiciones relativas de los ojos en la cabeza
        # Imágenes para la cabeza, cuerpo y cola de la serpiente
        self.head_image = load_and_scale_image("assets/imagenes/cabeza2.png", (23, 24))
        self.body_image = load_and_scale_image("assets/imagenes/body2.png", (21.5, 23))
        self.tail_image = load_and_scale_image("assets/imagenes/cola2.png", (21.5, 24))

    def move(self):
        # Mueve la serpiente en la dirección actual
        head_position = self.body[0] + self.direction * CELL_SIZE
        if self.growing:
            # Si la serpiente está creciendo, agrega una nueva cabeza al cuerpo
            self.body = [head_position] + self.body
            self.growing = False
        else:
            # Si no está creciendo, mueve la serpiente eliminando la cola
            self.body = [head_position] + self.body[:-1]

    def grow(self):
        # Indica que la serpiente debe crecer en el próximo movimiento
        self.growing = True

    def draw(self, screen):
        # Dibujar el cuerpo de la serpiente
        for segment in self.body[1:-1]:
            screen.blit(self.body_image, segment)

        # Rotar la cabeza de la serpiente según la dirección
        head_pos = self.body[0]
        rotated_head_image = pygame.transform.rotate(self.head_image, self.directions_to_angle())
        screen.blit(rotated_head_image, head_pos)

        # Dibujar la cola de la serpiente usando la imagen
        tail_pos = self.body[-1]
        opposite_direction = -self.direction
        rotated_tail_image = pygame.transform.rotate(self.tail_image, self.directions_to_angle(opposite_direction))
        screen.blit(rotated_tail_image, tail_pos)

        # Interpolación para suavizar la rotación de la cola
        tail_direction = self.body[-2] - self.body[-1]
        if tail_direction != pygame.Vector2(0, 0):
            tail_direction = tail_direction.normalize()
            angle = self.directions_to_angle(-tail_direction)
            rotated_tail_image = pygame.transform.rotate(self.tail_image, angle)
            screen.blit(rotated_tail_image, self.body[-1])

        # Dibujar ojos en la cabeza
        eye_offset = [(18, 10), (10, 10)] if self.direction.x == 0 else [(12, 5), (12, 15)]  # Nuevas posiciones de los ojos
        for offset in eye_offset:
            eye_pos = (head_pos[0] + offset[0], head_pos[1] + offset[1])
            pygame.draw.circle(screen, WHITE, eye_pos, 2)

    def directions_to_angle(self, direction=None):
        # Convierte la dirección de la serpiente en un ángulo para rotar la cabeza y la cola
        if direction is None:
            direction = self.direction
        if direction == pygame.Vector2(1, 0):
            return 270
        elif direction == pygame.Vector2(-1, 0):
            return 90
        elif direction == pygame.Vector2(0, -1):
            return 0
        elif direction == pygame.Vector2(0, 1):
            return 180

    def change_direction(self, direction):
        # Cambia la dirección de la serpiente si es una dirección válida y no está en la dirección opuesta
        if direction in self.directions:
            new_direction = self.directions[direction]
            opposite_direction = -self.direction
            if new_direction != opposite_direction:
                self.direction = new_direction

# Clase para obstáculos
class Obstacle(GameObject):
    def __init__(self, position):
        super().__init__(position)  #llama al medodo posiccion dela clase padre o base (GameObject) para inicializar la posición de los obstaculos
        self.image = load_and_scale_image('assets/imagenes/depositphotos_54217117-stock-photo-wood-crate-generated-hires-texture.jpg', (23, 24))

    def draw(self, screen):
        screen.blit(self.image, self.position)

# Clase para elementos especiales
class SpecialItem(GameObject):
    def __init__(self, position):
        super().__init__(position) #llama al medodo posiccion dela clase padre o base (GameObject) para inicializar la posición de la comida especial
        self.timer = 200  # Duracion activa
        self.image = load_and_scale_image('assets/imagenes/Yellow-Apple-icon.png', (25, 25))

    def draw(self, screen):
        screen.blit(self.image, self.position)

# Clase para el juego
class Game:
    def __init__(self): #aqui se implementa un tipo de composicion ya que contiene instancias de Snake, Food, Obstacle y SpecialItem
         # Instancias de las clases snake,food,obstacles y Special_Item
        self.snake = Snake(pygame.Vector2(WIDTH // 2, HEIGHT // 2))
        self.food = self.place_food()
        self.obstacles = self.place_obstacles()
        self.special_item = None
        self.score = 0 # Puntuación del jugador
        self.special_item_timer = 0 # Temporizador para controlar la duración del objeto especial
        self.paused = False # Indica si el juego está pausado o no

    def place_food(self):
        #Genera la instancia de comida en una posicion aleatoria
        return self.place_random_object(Food)

    def place_obstacles(self):
        #Genera una lista de instancias de obstaculos en posiciones aleatorias
        obstacles = []
        occupied_positions = set(tuple(seg) for seg in self.snake.body)  # posiciones ocupadas por la serpiente
        occupied_positions.add(tuple(self.food.position))  # posición ocupada por la comida
        while len(obstacles) < 15:  # número de obstáculos
            x = random.randint(0, (WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
            y = random.randint(0, (HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
            new_position = (x, y)
            if new_position not in occupied_positions:
                obstacles.append(Obstacle(pygame.Vector2(x, y)))
                occupied_positions.add(new_position)
        return obstacles

    def place_special_item(self):
        #Genera la instancia de objeto especial en una posicion aleatoria
        return self.place_random_object(SpecialItem)

    def place_random_object(self, obj_type, occupied_positions=None):
        # Genera la instancia de un objeto de tipo obj_type en una posición aleatoria
        if occupied_positions is None:
            occupied_positions = set(tuple(seg) for seg in self.snake.body)  # posiciones ocupadas por la serpiente

        while True: # Bucle infinito para generar una posición aleatoria
            x = random.randint(0, (WIDTH - CELL_SIZE) // CELL_SIZE - 1) * CELL_SIZE # Genera una coordenada x aleatoria, asegurándose de que esté alineada con la cuadrícula del juego
            y = random.randint(0, (HEIGHT - CELL_SIZE) // CELL_SIZE - 1) * CELL_SIZE # Genera una coordenada y aleatoria, asegurándose de que esté alineada con la cuadrícula del juego
            new_position = (x, y) # Crea una nueva posición con las coordenadas generadas
            if new_position not in occupied_positions: # Verifica si la nueva posición no está ocupada por ningún otro objeto
                return obj_type(pygame.Vector2(x, y)) # Crea una instancia del objeto en la nueva posición

    #Verifica las colisiones entre elementos del juego y maneja las interacciones
    def check_collision(self):
        # Si la cabeza de la serpiente alcanza la comida, la serpiente crece y se genera una nueva comida
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.food = self.place_food()
            self.score += 10
            # Hay una probabilidad del 20% de generar un objeto especial si no hay uno en el juego
            if random.randint(0, 100) < 20 and self.special_item is None:
                self.special_item = self.place_special_item()

        # Si la cabeza de la serpiente alcanza un objeto especial, se activa y se elimina del juego
        if self.special_item and self.snake.body[0] == self.special_item.position:
            self.special_item
            self.special_item = None
            self.snake.speed_boost = True
            self.special_item_timer = 200 # Duración activa del objeto especial 
        
        # Verificar colisión con los bordes de la pantalla
        if self.snake.body[0].x < 0 or self.snake.body[0].x >= WIDTH or self.snake.body[0].y < 0 or self.snake.body[0].y >= HEIGHT:
            return True
        
        # Verificar colisión con el cuerpo de la serpiente
        if len(self.snake.body) != len(set(tuple(segment) for segment in self.snake.body)):
            return True
        
        # Verificar colisión con obstáculos
        for obstacle in self.obstacles:
            if self.snake.body[0] == obstacle.position:
                return True

        return False

    #Actualiza el estado del juego en cada fotograma
    def update(self):
        if self.snake.speed_boost:
            self.snake.move()
        self.snake.move()
        if self.special_item_timer > 0:
            self.special_item_timer -= 1
        else:
            self.snake.speed_boost = False
        return self.check_collision()
    
    #Dibuja todos los elementos del juego en la pantalla
    def draw(self, screen):
        background_image = pygame.image.load("assets/imagenes/R.jpeg")
        screen.blit(background_image, (0, 0))  # Dibujar la imagen de fondo
        self.snake.draw(screen) # Dibujar la serpiente
        self.food.draw(screen) # Dibujar la comida
        for obstacle in self.obstacles:
            obstacle.draw(screen) # Dibujar los obstáculos
        if self.special_item:
            self.special_item.draw(screen) # Dibujar el objeto especial si está presente
        self.draw_score(screen) # Dibujar la puntuación en pantalla
        pygame.display.flip()

    #Dibuja la puntuación en la pantalla
    def draw_score(self, screen):
        score_text = font.render(f'Puntuación: {self.score}', True, WHITE)
        screen.blit(score_text, [10, 10])

# Pantalla de inicio
def show_start_screen():
    background_img = pygame.image.load("assets/imagenes/inicio.png")
    
    screen.blit(background_img, (-15, -25))
    title = font.render('Presione cualquier tecla para comenzar', True, WHITE)
    screen.blit(title, [WIDTH // 4 - 40, HEIGHT // 2 + 250])
    pygame.display.flip() # Actualiza la pantalla
    wait_for_key() # Espera a que el jugador presione una tecla para continuar

# Pantalla de fin de juego
def show_game_over_screen(score):
    screen.fill(BLACK) # Rellena la pantalla con color negro
    # Calcula las dimensiones de los textos
    game_over_text = font.render('Game Over', True, RED)
    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))

    score_text = font.render(f'Tu puntaje: {score}', True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    restart_text1 = font.render('Presiona cualquier tecla', True, WHITE)
    restart_rect1 = restart_text1.get_rect(center=(WIDTH // 2, HEIGHT // 1.5))

    restart_text2 = font.render('para reiniciar el juego', True, WHITE)
    restart_rect2 = restart_text2.get_rect(center=(WIDTH // 2, HEIGHT // 1.5 + 40))

    # Coloca los textos en la pantalla en posiciones específicas
    screen.blit(game_over_text, game_over_rect)
    screen.blit(score_text, score_rect)
    screen.blit(restart_text1, restart_rect1)
    screen.blit(restart_text2, restart_rect2)

    pygame.display.flip() # Actualiza la pantalla
    wait_for_key() # Espera a que el jugador presione una tecla para reiniciar el juego

# Espera por una tecla para continuar
def wait_for_key():
    waiting = True # Variable para controlar el bucle de espera
    while waiting:
        for event in pygame.event.get(): # Itera sobre los eventos en la cola de eventos
            if event.type == pygame.QUIT: # Si se presiona el botón de cerrar ventana
                pygame.quit() # Cierra pygame
                exit() # Sale del programa
            elif event.type == pygame.KEYDOWN: # Si se presiona una tecla
                waiting = False # Sale del bucle de espera
        pygame.time.wait(100)  # Espera 100ms entre iteraciones para reducir el uso de la CPU espera de una tecla en la pantalla de inicio o game over

# Bucle principal del juego
def main():
    clock = pygame.time.Clock() # Objeto para controlar el tiempo del juego
    game = Game() # Inicializa el juego

    show_start_screen() # Muestra la pantalla de inicio al inicio del juego

    running = True  # Variable para controlar el bucle principal del juego
    while running:
        for event in pygame.event.get(): # Itera sobre los eventos en la cola de eventos
            if event.type == pygame.QUIT: # Si se presiona el botón de cerrar ventana
                running = False # Sale del bucle principal del juego
            elif event.type == pygame.KEYDOWN: # Si se presiona una tecla
                if event.key == pygame.K_SPACE: # Si se presiona la barra espaciadora
                    game.paused = not game.paused # Pausa o reanuda el juego
                elif not game.paused: # Si el juego no está pausado
                    # Cambia la dirección de la serpiente según la tecla presionada por el jugador
                    if event.key == pygame.K_w:
                        game.snake.change_direction('UP')
                    elif event.key == pygame.K_s:
                        game.snake.change_direction('DOWN')
                    elif event.key == pygame.K_a:
                        game.snake.change_direction('LEFT')
                    elif event.key == pygame.K_d:
                        game.snake.change_direction('RIGHT')

        if not game.paused: # Si el juego no está pausado
            if game.update(): # Actualiza el estado del juego y verifica si ha terminado
                show_game_over_screen(game.score) # Muestra la pantalla de fin de juego con la puntuación
                game = Game() # Reinicia el juego
                show_start_screen() # Muestra la pantalla de inicio nuevamente

            game.draw(screen) # Dibuja los elementos del juego en la pantalla
            clock.tick(FPS + game.score // 50) # Controla la velocidad del juego según la puntuación del jugador
        else:
            # Muestra un mensaje de juego pausado en la pantalla
            paused_text = font.render('Juego Pausado', True, WHITE)
            screen.blit(paused_text, [WIDTH // 2.5, HEIGHT // 2.5])
            pygame.display.flip() # Actualiza la pantalla
            pygame.time.wait(100)  # Espera 100ms entre iteraciones para reducir el uso de la CPU cuando el juego está pausado

if __name__ == '__main__':
    main() # Ejecuta el bucle principal del juego  
