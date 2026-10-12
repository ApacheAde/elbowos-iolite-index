#!/usr/bin/env python3
"""Iolite Index — neon letter-catch word arcade for ElbowOS. Python 3 + pygame."""
import math, os, random, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/IOLITE_INDEX_ElbowOS.mp4")
TITLE, HANDLE = "IOLITE INDEX", "x.com/ElbowOS"

VOID = (8, 4, 22)
INK = (18, 8, 42)
VIOLET = (140, 60, 255)
CYAN = (40, 230, 255)
GOLD = (255, 210, 60)
MAG = (255, 50, 180)
WHITE = (240, 245, 255)
LIME = (120, 255, 140)

WORDS = ["NEON", "CODE", "PYTH", "ELBO", "OS", "GAME", "REEL", "ARCADE", "PIXEL", "GLOW"]

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.quit()
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H), pygame.HIDDEN)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("dejavusans", 72, bold=True)
        self.small = pygame.font.SysFont("dejavusans", 42, bold=True)
        self.tiny = pygame.font.SysFont("dejavusans", 28, bold=True)
        self.reset()

    def reset(self):
        self.score = 0
        self.word_i = 0
        self.progress = 0
        self.letters = []
        self.paddle_x = W // 2
        self.spawn_t = 0
        self.flash = 0
        self.combo = 0
        self.t = 0

    def current_word(self):
        return WORDS[self.word_i % len(WORDS)]

    def next_letter(self):
        w = self.current_word()
        return w[self.progress] if self.progress < len(w) else None

    def spawn(self):
        if random.random() < 0.55:
            ch = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        else:
            nl = self.next_letter()
            ch = nl if nl else random.choice("ABCDEFG")
        x = random.randint(80, W - 80)
        self.letters.append({"x": x, "y": -40, "ch": ch, "vy": random.uniform(7, 12), "glow": random.uniform(0, 6)})

    def update(self, dt, auto=False):
        self.t += dt
        self.spawn_t += dt
        if self.spawn_t > 0.35:
            self.spawn()
            self.spawn_t = 0
        if self.flash > 0:
            self.flash -= dt
        # paddle AI or keys
        target = None
        if auto:
            nl = self.next_letter()
            best = None
            for L in self.letters:
                if L["ch"] == nl and L["y"] > 200:
                    if best is None or L["y"] > best["y"]:
                        best = L
            if best:
                target = best["x"]
            else:
                target = W // 2
            self.paddle_x += (target - self.paddle_x) * 0.18
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.paddle_x -= 18
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.paddle_x += 18
        self.paddle_x = max(60, min(W - 60, self.paddle_x))
        # letters
        catch_y = H - 220
        for L in self.letters[:]:
            L["y"] += L["vy"]
            L["glow"] += dt * 8
            if L["y"] > catch_y and abs(L["x"] - self.paddle_x) < 70:
                nl = self.next_letter()
                if L["ch"] == nl:
                    self.score += 10 + self.combo * 2
                    self.combo += 1
                    self.progress += 1
                    self.flash = 0.25
                    if self.progress >= len(self.current_word()):
                        self.score += 50
                        self.word_i += 1
                        self.progress = 0
                        self.combo = 0
                else:
                    self.combo = 0
                self.letters.remove(L)
            elif L["y"] > H + 40:
                self.letters.remove(L)
                self.combo = 0

    def draw(self, surf):
        surf.fill(VOID)
        # bg glow bands
        for i in range(6):
            y = (self.t * 80 + i * 320) % (H + 200) - 100
            col = (VIOLET[0]//4, VIOLET[1]//6, VIOLET[2]//3)
            pygame.draw.rect(surf, col, (0, y, W, 40), border_radius=8)
        # title
        title = self.font.render(TITLE, True, CYAN)
        surf.blit(title, title.get_rect(center=(W//2, 90)))
        handle = self.small.render(HANDLE, True, GOLD)
        surf.blit(handle, handle.get_rect(center=(W//2, 160)))
        # word display
        w = self.current_word()
        shown = w[:self.progress] + ("_" * (len(w) - self.progress))
        wr = self.font.render(shown, True, WHITE if self.flash <= 0 else LIME)
        surf.blit(wr, wr.get_rect(center=(W//2, 280)))
        # score
        sc = self.small.render(f"SCORE {self.score}", True, MAG)
        surf.blit(sc, sc.get_rect(center=(W//2, 360)))
        # paddle
        px = int(self.paddle_x)
        pygame.draw.rect(surf, CYAN, (px - 70, H - 200, 140, 28), border_radius=14)
        pygame.draw.rect(surf, GOLD, (px - 50, H - 194, 100, 16), border_radius=8)
        # letters
        for L in self.letters:
            g = 0.6 + 0.4 * math.sin(L["glow"])
            col = (int(CYAN[0]*g), int(CYAN[1]*g), int(CYAN[2]*g)) if L["ch"] == self.next_letter() else (int(VIOLET[0]*g), int(VIOLET[1]*g), int(VIOLET[2]*g))
            r = 36
            pygame.draw.circle(surf, col, (int(L["x"]), int(L["y"])), r)
            pygame.draw.circle(surf, WHITE, (int(L["x"]), int(L["y"])), r, 3)
            lt = self.small.render(L["ch"], True, WHITE)
            surf.blit(lt, lt.get_rect(center=(int(L["x"]), int(L["y"]))))
        # bottom bar
        pygame.draw.rect(surf, INK, (0, H - 80, W, 80))
        tip = self.tiny.render("A/D or arrows — catch next letter", True, WHITE)
        surf.blit(tip, tip.get_rect(center=(W//2, H - 40)))

    def play_interactive(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for e in pygame.event.get():
                if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                    running = False
                if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                    self.reset()
            self.update(dt, auto=False)
            self.draw(self.screen)
            pygame.display.flip()
        pygame.quit()

    def record(self):
        frames = FPS * SECS
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
            "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS),
            "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-preset", "fast", "-movflags", "+faststart",
            OUT
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            for i in range(frames):
                dt = 1.0 / FPS
                self.update(dt, auto=True)
                self.draw(self.screen)
                raw = pygame.image.tostring(self.screen, "RGB")
                proc.stdin.write(raw)
            proc.stdin.close()
            err = proc.stderr.read().decode("utf-8", "ignore")
            rc = proc.wait()
            if rc != 0:
                raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1500:]}")
            print("wrote", OUT)
        finally:
            pygame.quit()

def main():
    g = Game()
    if PLAY and not RECORD:
        g.play_interactive()
    else:
        g.record()

if __name__ == "__main__":
    main()
