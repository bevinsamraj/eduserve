def recommend_resources(weakest_subject):
    """
    Provides a dictionary of detailed recommended resources for a student's weakest subject,
    including websites, videos, and reading materials with descriptions.
    """
    resources = {
        "Math": {
            "websites": [
                {"name": "Khan Academy", "url": "https://www.khanacademy.org/math", "description": "Comprehensive lessons, practice exercises, and quizzes for all math levels."},
                {"name": "Brilliant.org", "url": "https://brilliant.org/courses/math-foundations/", "description": "Interactive problem-solving to build quantitative and mathematical intuition."},
            ],
            "videos": [
                {"name": "3Blue1Brown: Essence of Algebra", "embed_url": "https://www.youtube.com/embed/videoseries?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab"},
                {"name": "The Organic Chemistry Tutor: Algebra Basics", "embed_url": "https://www.youtube.com/embed/NybHckSEQBI"},
            ],
            "reading": [
                {"name": "OpenStax: Algebra and Trigonometry", "description": "A free, peer-reviewed online textbook covering core concepts."},
            ]
        },
        "Science": {
            "websites": [
                {"name": "PhET Interactive Simulations", "url": "https://phet.colorado.edu/", "description": "Fun, free, interactive, research-based science and mathematics simulations."},
                {"name": "NASA Science", "url": "https://science.nasa.gov/", "description": "Explore the latest news, images, and discoveries from NASA's science missions."},
            ],
            "videos": [
                {"name": "CrashCourse Physics", "embed_url": "https://www.youtube.com/embed/videoseries?list=PL8dPuuaLjXtN0ge7yDk_UA0ldZJdhwkoV"},
                {"name": "Kurzgesagt – In a Nutshell", "embed_url": "https://www.youtube.com/embed/0fKBhvDjuy0"},
            ],
            "reading": [
                {"name": "National Geographic Science", "description": "In-depth articles on everything from space exploration to animal behavior."},
            ]
        },
        "English": {
            "websites": [
                {"name": "Purdue Online Writing Lab (OWL)", "url": "https://owl.purdue.edu/", "description": "A comprehensive resource for writing, grammar, and citation style guides."},
                {"name": "Grammarly Blog", "url": "https://www.grammarly.com/blog/", "description": "Tips and articles on grammar, spelling, punctuation, and effective writing."},
            ],
            "videos": [
                {"name": "CrashCourse Literature", "embed_url": "https://www.youtube.com/embed/videoseries?list=PL8dPuuaLjXtOeEc9_iFq5v9-e_z2deA4-"},
                {"name": "TED-Ed: Riddles", "embed_url": "https://www.youtube.com/embed/videoseries?list=PLJicmE8fK0Ei_6i2gL3r11S-n5x_s_4_i"},
            ],
            "reading": [
                {"name": "Project Gutenberg", "description": "A library of over 60,000 free eBooks, including many classic literature titles."},
            ]
        },
        "History": {
            "websites": [
                {"name": "History.com", "url": "https://www.history.com/", "description": "Watch full episodes of your favorite HISTORY shows and read articles on historical events."},
                {"name": "World History Encyclopedia", "url": "https://www.worldhistory.org/", "description": "Peer-reviewed articles, maps, and timelines covering all periods of world history."},
            ],
            "videos": [
                {"name": "CrashCourse World History", "embed_url": "https://www.youtube.com/embed/videoseries?list=PLBDA2E52FB1EF80C9"},
                {"name": "OverSimplified", "embed_url": "https://www.youtube.com/embed/2N_g5jTT2_A"},
            ],
            "reading": [
                {"name": "The Gilder Lehrman Institute of American History", "description": "Primary sources, essays, and multimedia on American history."},
            ]
        },
        "Art": {
            "websites": [
                {"name": "Google Arts & Culture", "url": "https://artsandculture.google.com/", "description": "Explore high-resolution images and stories from cultural institutions around the world."},
                {"name": "Artcyclopedia", "url": "http://www.artcyclopedia.com/", "description": "A comprehensive index of online museum-quality art."},
            ],
            "videos": [
                {"name": "The Art Assignment (PBS)", "embed_url": "https://www.youtube.com/embed/videoseries?list=PL_w_qxa-x-4Vb950a3q2b-c8g5a4-C_4"},
                {"name": "Tate: How to Paint Like...", "embed_url": "https://www.youtube.com/embed/videoseries?list=PLvAS0-niOb-0o0Gbo51sPLV9G0aO3uK7m"},
            ],
            "reading": [
                {"name": "The Metropolitan Museum of Art's Heilbrunn Timeline of Art History", "description": "Thematic essays, chronologies, and works of art from the Met's collection."},
            ]
        }
    }
    
    return resources.get(weakest_subject, None)