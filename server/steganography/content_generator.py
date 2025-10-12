"""
🎨 Algorithmic Content Generator
Creates innocent-looking content using pure mathematics - NO AI TOKENS REQUIRED!
"""

import random
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from datetime import datetime
import colorsys

class ContentGenerator:
    """Generate innocent-looking content algorithmically"""
    
    def __init__(self):
        self.seed_generator = random.Random()
        
    def generate_fractal_image(self, width=512, height=512, seed=None):
        """
        🌀 Generate beautiful fractal art using Mandelbrot set
        Creates stunning visuals that look AI-generated but cost $0!
        """
        if seed:
            random.seed(seed)
            
        img = Image.new('RGB', (width, height))
        pixels = img.load()
        
        # Mandelbrot parameters
        zoom = random.uniform(150, 300)
        cx = random.uniform(-0.8, 0.3)
        cy = random.uniform(-0.3, 0.3)
        max_iter = 80
        
        print(f"🎨 Generating fractal art ({width}x{height}) with zoom={zoom:.1f}")
        
        for x in range(width):
            for y in range(height):
                # Convert pixel to complex plane
                zx = (x - width/2) / zoom + cx
                zy = (y - height/2) / zoom + cy
                
                # Mandelbrot iteration
                c = complex(zx, zy)
                z = 0
                
                for i in range(max_iter):
                    if abs(z) > 2:
                        break
                    z = z*z + c
                
                # Create beautiful color based on iteration count
                if i == max_iter:
                    color = (0, 0, 0)  # Inside set = black
                else:
                    # Rainbow color based on escape time
                    hue = (i / max_iter) * 360
                    saturation = 0.8
                    value = 0.9 if i < max_iter else 0
                    
                    rgb = colorsys.hsv_to_rgb(hue/360, saturation, value)
                    color = tuple(int(255 * c) for c in rgb)
                
                pixels[x, y] = color
        
        print("✅ Fractal image generated successfully!")
        return img
    
    def generate_gradient_image(self, width=512, height=512, seed=None):
        """
        🌈 Generate beautiful gradient patterns
        Creates abstract art perfect for hiding data
        """
        if seed:
            random.seed(seed)
            
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Random gradient colors
        color1 = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        color2 = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        
        gradient_type = random.choice(['linear', 'radial', 'diagonal'])
        
        print(f"🎨 Generating {gradient_type} gradient from {color1} to {color2}")
        
        if gradient_type == 'linear':
            # Horizontal gradient
            for x in range(width):
                ratio = x / width
                r = int(color1[0] * (1-ratio) + color2[0] * ratio)
                g = int(color1[1] * (1-ratio) + color2[1] * ratio)
                b = int(color1[2] * (1-ratio) + color2[2] * ratio)
                draw.line([(x, 0), (x, height)], fill=(r, g, b))
                
        elif gradient_type == 'radial':
            # Radial gradient from center
            center_x, center_y = width//2, height//2
            max_distance = math.sqrt(center_x**2 + center_y**2)
            
            for x in range(width):
                for y in range(height):
                    distance = math.sqrt((x-center_x)**2 + (y-center_y)**2)
                    ratio = min(distance / max_distance, 1.0)
                    
                    r = int(color1[0] * (1-ratio) + color2[0] * ratio)
                    g = int(color1[1] * (1-ratio) + color2[1] * ratio)
                    b = int(color1[2] * (1-ratio) + color2[2] * ratio)
                    draw.point([(x, y)], fill=(r, g, b))
        
        # Add some noise for natural look
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        print("✅ Gradient image generated successfully!")
        return img
    
    def generate_noise_pattern(self, width=512, height=512, seed=None):
        """
        🌊 Generate Perlin noise patterns
        Creates natural-looking textures perfect for steganography
        """
        if seed:
            np.random.seed(seed)
            
        print(f"🎨 Generating noise pattern ({width}x{height})")
        
        # Generate random noise
        noise = np.random.random((height, width))
        
        # Apply multiple octaves for natural look
        for octave in range(1, 4):
            scale = 2 ** octave
            octave_noise = np.random.random((height//scale, width//scale))
            octave_noise = np.repeat(np.repeat(octave_noise, scale, axis=0), scale, axis=1)
            
            # Trim to exact size
            octave_noise = octave_noise[:height, :width]
            noise += octave_noise * (0.5 ** octave)
        
        # Normalize and convert to image
        noise = (noise * 255).astype(np.uint8)
        
        # Convert to RGB with color variation
        img = Image.new('RGB', (width, height))
        pixels = img.load()
        
        for x in range(width):
            for y in range(height):
                value = noise[y, x]
                # Add slight color tint
                r = min(255, value + random.randint(-20, 20))
                g = min(255, value + random.randint(-20, 20))
                b = min(255, value + random.randint(-20, 20))
                pixels[x, y] = (max(0,r), max(0,g), max(0,b))
        
        print("✅ Noise pattern generated successfully!")
        return img
    
    def generate_innocent_text(self, length='medium', topic=None, seed=None):
        """
        📝 Generate innocent-looking text content
        Creates realistic conversations, stories, or descriptions
        """
        if seed:
            random.seed(seed)
            
        templates = {
            'weather': [
                "Today's weather forecast shows {condition} conditions with temperatures around {temp}°F. Perfect weather for {activity}!",
                "The {time_period} has been quite {weather_desc}. I noticed {observation} while walking outside.",
                "Weather update: {condition} skies expected through {time}. Great time to {suggestion}.",
                "Beautiful {condition} day today. Temperature feels just right at {temp} degrees. Perfect for {activity}.",
                "The weather this {time_period} has been absolutely {weather_desc}. Saw some {observation} earlier.",
                "Checking the forecast - looks like {condition} weather continuing through {time}. Time to {suggestion}!"
            ],
            'daily_life': [
                "Had an interesting {time_period} today. Went to the {location} and saw {observation}. Really made me think about {topic}.",
                "Just finished reading about {subject} and found it fascinating how {insight}. Planning to {future_action} soon.",
                "The {event} reminded me of {memory}. It's amazing how {reflection} can {impact}.",
                "Started my {time_period} with a visit to the {location}. Noticed {observation} which got me thinking about {topic}.",
                "Been exploring {subject} lately and discovered {insight}. Really want to {future_action} next.",
                "That {event} brought back memories of {memory}. Funny how {reflection} always {impact}.",
                "Took a walk to the {location} this {time_period}. The {observation} was incredible. Made me appreciate {topic}.",
                "Reading up on {subject} has been eye-opening. The way {insight} is remarkable. Should {future_action} sometime.",
                "Had coffee at the local {location} today. Overheard someone discussing {subject} and {insight}. Might {future_action}.",
                "Spent the {time_period} at the {location} watching {observation}. Simple moments like these remind me about {topic}."
            ],
            'food': [
                "Tried a new {meal_type} recipe today with {ingredient1} and {ingredient2}. The flavor combination was {taste_desc}!",
                "The local {establishment} has the best {food_item}. Their secret ingredient seems to be {ingredient}.",
                "Cooking tip: {cooking_method} your {ingredient} for about {time} minutes adds amazing {quality}.",
                "Made {meal_type} using {ingredient1} and {ingredient2}. The result was surprisingly {taste_desc}!",
                "Discovered this great {establishment} that serves incredible {food_item}. They use {ingredient} which makes it {taste_desc}.",
                "Learned a new cooking technique: {cooking_method} the {ingredient} for {time} minutes creates {quality} texture.",
                "Experimented with {ingredient1} and {ingredient2} in my {meal_type} today. Turned out {taste_desc} than expected!",
                "Found the perfect {establishment} for {food_item}. Their use of {ingredient} gives it that {quality} taste."
            ],
            'technology': [
                "Just learned about {tech_topic} and how it {impact} in {field}. The possibilities for {application} are endless!",
                "The new {device} update includes {feature} which makes {task} much more {improvement}.",
                "Interesting article about {tech_concept} and its role in {domain}. Could revolutionize {area}.",
                "Been reading about {tech_topic} and its {impact} on {field}. Amazing potential for {application}!",
                "The latest {device} features {feature} that really helps with {task}. Makes everything more {improvement}.",
                "Fascinating piece on {tech_concept} and how it's changing {domain}. This could transform {area} completely.",
                "Discovered {tech_topic} recently and learned how it {impact} across {field}. Great opportunities for {application}.",
                "Updated my {device} and love the new {feature}. It makes {task} so much more {improvement} than before."
            ],
            'casual': [
                "Hope you're having a great {time_period}! I was just thinking about {topic} and wanted to share some thoughts.",
                "How's your {time_period} going? I've been {activity} and it's been really {feeling}. What are you up to?",
                "Just wanted to check in and see how things are going. Been {activity} myself and feeling quite {feeling}.",
                "Hey there! Having a {feeling} {time_period} so far. Spent some time {activity} which was really nice.",
                "Good {time_period}! Been thinking about our last conversation regarding {topic}. Hope your day is going well.",
                "Hi! Just finished {activity} and thought I'd drop a quick message. How has your {time_period} been?",
                "Hello! Having a wonderfully {feeling} {time_period}. Been {activity} and really enjoying it. Hope you're well!",
                "Hey! Just wanted to say hi and see how you're doing. My {time_period} has been pretty {feeling} so far.",
                "Hi there! Quick check-in to see how things are. I've been {activity} and it's been quite {feeling}.",
                "Hello! Hope your {time_period} is treating you well. I've been {activity} and thinking about {topic}."
            ]
        }
        
        # Choose random template category
        if not topic:
            topic = random.choice(list(templates.keys()))
        
        template = random.choice(templates.get(topic, templates['daily_life']))
        
        # Fill template with random content
        replacements = {
            'condition': random.choice(['sunny', 'cloudy', 'partly cloudy', 'clear', 'mild']),
            'temp': random.randint(65, 85),
            'activity': random.choice(['outdoor activities', 'a walk', 'gardening', 'reading outside', 'reading', 'writing', 'cooking', 'listening to music', 'exercising', 'studying']),
            'time_period': random.choice(['morning', 'afternoon', 'evening', 'day', 'week']),
            'weather_desc': random.choice(['pleasant', 'refreshing', 'comfortable', 'nice', 'lovely']),
            'observation': random.choice(['interesting cloud formations', 'beautiful flowers blooming', 'people enjoying the outdoors', 'birds singing']),
            'time': random.choice(['the weekend', 'tomorrow', 'this week', 'the next few days']),
            'suggestion': random.choice(['enjoy nature', 'take photos', 'spend time outside', 'appreciate the beauty']),
            'location': random.choice(['park', 'library', 'market', 'café', 'bookstore', 'museum']),
            'topic': random.choice(['life', 'nature', 'creativity', 'learning', 'growth', 'beauty', 'friendship', 'work', 'hobbies', 'plans']),
            'subject': random.choice(['history', 'science', 'art', 'philosophy', 'literature', 'culture']),
            'insight': random.choice(['innovation works', 'people connect', 'ideas develop', 'creativity flows']),
            'future_action': random.choice(['explore more', 'learn about it', 'try something new', 'share this knowledge']),
            'event': random.choice(['conversation', 'experience', 'book', 'documentary', 'article']),
            'memory': random.choice(['childhood', 'school days', 'a good friend', 'family time', 'travel']),
            'reflection': random.choice(['memories', 'experiences', 'learning', 'growth', 'connections']),
            'impact': random.choice(['inspire us', 'teach us', 'motivate us', 'guide us', 'help us grow']),
            'feeling': random.choice(['great', 'wonderful', 'pleasant', 'relaxing', 'productive', 'peaceful', 'enjoyable', 'nice']),
            'meal_type': random.choice(['breakfast', 'lunch', 'dinner', 'snack', 'dish']),
            'ingredient1': random.choice(['tomatoes', 'onions', 'garlic', 'herbs', 'spices', 'vegetables']),
            'ingredient2': random.choice(['cheese', 'pasta', 'rice', 'bread', 'sauce', 'seasoning']),
            'taste_desc': random.choice(['delicious', 'amazing', 'flavorful', 'satisfying', 'tasty', 'wonderful']),
            'establishment': random.choice(['café', 'restaurant', 'bakery', 'deli', 'bistro', 'place']),
            'food_item': random.choice(['coffee', 'sandwich', 'pizza', 'salad', 'soup', 'pastry']),
            'ingredient': random.choice(['fresh herbs', 'special sauce', 'quality ingredients', 'homemade dressing']),
            'cooking_method': random.choice(['sautéing', 'roasting', 'grilling', 'steaming', 'baking']),
            'time': random.choice(['5', '10', '15', '20', '25']),
            'quality': random.choice(['rich', 'crispy', 'tender', 'flavorful', 'perfect']),
            'tech_topic': random.choice(['automation', 'digital tools', 'online platforms', 'mobile apps']),
            'field': random.choice(['education', 'business', 'communication', 'daily life']),
            'application': random.choice(['learning', 'productivity', 'entertainment', 'connection']),
            'device': random.choice(['phone', 'computer', 'tablet', 'app']),
            'feature': random.choice(['improved interface', 'better performance', 'new functionality', 'enhanced security']),
            'task': random.choice(['communication', 'organization', 'productivity', 'entertainment']),
            'improvement': random.choice(['efficient', 'convenient', 'user-friendly', 'reliable']),
            'tech_concept': random.choice(['cloud computing', 'artificial intelligence', 'mobile technology', 'digital communication']),
            'domain': random.choice(['workplace', 'education', 'personal life', 'society']),
            'area': random.choice(['how we work', 'how we learn', 'how we connect', 'daily routines'])
        }
        
        # Generate text
        text = template.format(**{k: v for k, v in replacements.items() if '{' + k + '}' in template})
        
        # Add more content for longer texts
        if length == 'long':
            text += " " + self.generate_innocent_text('medium', topic, seed)
        
        print(f"📝 Generated innocent text ({len(text)} chars): '{text[:50]}...'")
        return text
    
    def generate_ambient_audio(self, duration=5.0, sample_rate=44100, seed=None):
        """
        🎵 Generate natural-sounding ambient audio
        Creates peaceful sounds perfect for hiding data
        """
        if seed:
            np.random.seed(seed)
            
        print(f"🎵 Generating ambient audio ({duration}s at {sample_rate}Hz)")
        
        t = np.linspace(0, duration, int(duration * sample_rate))
        audio = np.zeros_like(t)
        
        # Base ambient tone (like wind)
        base_freq = random.uniform(80, 120)
        audio += 0.1 * np.sin(2 * np.pi * base_freq * t)
        
        # Add harmonics
        for harmonic in range(2, 6):
            freq = base_freq * harmonic
            amplitude = 0.1 / harmonic
            audio += amplitude * np.sin(2 * np.pi * freq * t + random.uniform(0, 2*np.pi))
        
        # Add natural noise (like leaves rustling)
        audio += 0.05 * np.random.normal(0, 1, len(t))
        
        # Add some gentle "waves" (like distant water)
        wave_freq = random.uniform(0.5, 2.0)
        audio += 0.03 * np.sin(2 * np.pi * wave_freq * t)
        
        # Normalize to prevent clipping
        audio = audio / np.max(np.abs(audio)) * 0.8
        
        print("✅ Ambient audio generated successfully!")
        return audio, sample_rate

# Test the generator
if __name__ == "__main__":
    generator = ContentGenerator()
    
    # Test image generation
    img = generator.generate_fractal_image(256, 256)
    img.save("test_fractal.png")
    
    # Test text generation  
    text = generator.generate_innocent_text()
    print(f"Generated text: {text}")
    
    # Test audio generation
    audio, sr = generator.generate_ambient_audio(duration=2.0)
    print(f"Generated audio: {len(audio)} samples at {sr}Hz")