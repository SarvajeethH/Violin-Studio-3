import streamlit as st
import time
import io
import wave
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pydub import AudioSegment

# --- THE COMPLETE DATABASE (NO ABBREVIATIONS) ---
pieceDatabase = {
    "elgar_salut_damour": { "composer": "Edward Elgar", "title": "Salut d'amour, Op. 12", "keywords": ["elgar", "love's greeting"], "duration": "03:13", "description": "Composed as an engagement present to his future wife, 'Salut d'amour' (Love's Greeting) is one of Edward Elgar's most beloved short pieces. It is a heartfelt and lyrical romance that captures a sense of gentle affection and warmth. The graceful melody requires a pure, singing tone and sincere expression from the performer. It remains a popular encore piece and a staple of the light classical repertoire, showcasing Elgar's gift for melody.", "usualTempo": 66, "practiceTempo": 54 },
    "chopin_nocturne_op9_no2": { "composer": "Frédéric Chopin", "title": "Nocturne in E-flat Major, Op. 9 No. 2", "keywords": ["chopin", "nocturne", "op9", "no2"], "duration": "04:41", "description": "Arguably the most famous of all his nocturnes, this piece is a quintessential example of the Romantic piano style, here beautifully transcribed for violin. The main theme is a deeply lyrical and ornamented melody that flows with grace and elegance. It requires a beautiful, singing tone and a flexible sense of rhythm (rubato) to capture its poetic nature. The piece's structure is relatively simple, allowing the performer to focus on expressive phrasing and delicate nuance.", "usualTempo": 60, "practiceTempo": 50 },
    "debussy_clair_de_lune": { "composer": "Claude Debussy", "title": "Clair de Lune", "keywords": ["debussy", "bergamasque"], "duration": "04:38", "description": "The third and most celebrated movement of the 'Suite bergamasque,' 'Clair de Lune' is one of the most iconic pieces of Impressionist music. Its name, meaning 'moonlight,' perfectly captures the music's delicate, atmospheric, and dreamlike quality. The piece requires exceptional control over dynamics and tone color to create its shimmering textures. The fluid, almost improvisatory-sounding melody floats above rich and innovative harmonies, evoking a serene and magical nighttime scene.", "usualTempo": 50, "practiceTempo": 40 },
    "debussy_fille_cheveux_lin": { "composer": "Claude Debussy", "title": "La Fille aux Cheveux de Lin", "keywords": ["debussy", "flaxen hair"], "duration": "03:03", "description": "This piece, whose title means 'The Girl with the Flaxen Hair,' is the eighth prelude from Debussy's first book of Préludes. It is a work of simple, tender beauty, characterized by a gentle and lyrical melody. The music is known for its use of pentatonic scales, which gives it a folk-like, innocent quality. Performing this piece requires a pure, sweet tone and a delicate touch to convey its sense of peaceful intimacy and serene beauty.", "usualTempo": 66, "practiceTempo": 54 },
    "chopin_nocturne_op9_no1": { "composer": "Frédéric Chopin", "title": "Nocturne in B-flat Minor, Op. 9 No. 1", "keywords": ["chopin", "nocturne", "op9", "no1"], "duration": "06:06", "description": "The first nocturne in Chopin's Op. 9 set, this piece is more melancholic and introspective than its famous E-flat major sibling. It features a beautifully longing melody that unfolds over a steady left-hand accompaniment. The piece has a more dramatic and passionate middle section before returning to the calm, reflective mood of the opening. It demands a deep understanding of musical phrasing and the ability to convey a wide range of emotions with a controlled, beautiful tone.", "usualTempo": 84, "practiceTempo": 68 },
    "chopin_nocturne_c_sharp_minor": { "composer": "Frédéric Chopin", "title": "Nocturne in C-sharp Minor, B. 49", "keywords": ["chopin", "posthumous", "milstein"], "duration": "04:12", "description": "Composed in his youth but published after his death, this Nocturne in C-sharp Minor is one of Chopin's most beloved works. It is filled with a sense of dramatic pathos and profound melancholy, often nicknamed 'Reminiscence.' The piece builds from a quiet, somber opening to a powerful and passionate climax before fading away. Famous violin transcriptions, like the one by Nathan Milstein, capture the work's intense lyrical drama and virtuosic flair.", "usualTempo": 63, "practiceTempo": 52 },
    "debussy_beau_soir": { "composer": "Claude Debussy", "title": "Beau Soir", "keywords": ["debussy", "heifetz"], "duration": "02:21", "description": "'Beau Soir' (Beautiful Evening) is an early song by Claude Debussy, set to a poem by Paul Bourget, famously transcribed for violin by Jascha Heifetz. The music beautifully captures the poem's reflection on the fleeting beauty of life, comparing a sunset to the end of a day. It requires a warm, rich tone and a seamless legato to spin out its long, flowing melodic lines. The piece is a masterpiece of subtle expression, evoking a feeling of serene and gentle nostalgia.", "usualTempo": 58, "practiceTempo": 48 },
    "saint-saens_mon_coeur": { "composer": "Camille Saint-Saëns", "title": "Mon cœur s'ouvre à ta voix", "keywords": ["saint-saens", "samson", "delilah"], "duration": "05:59", "description": "This piece is a famous aria from the opera 'Samson and Delilah,' with a title that translates to 'My heart opens to your voice.' It is sung by Delilah in Act II as she attempts to seduce Samson into revealing the secret of his strength. The music is incredibly lyrical, seductive, and filled with a sense of romantic passion. On the violin, it becomes a powerful showcase for a beautiful, rich tone and expressive, operatic phrasing.", "usualTempo": 54, "practiceTempo": 44 },
    "offenbach_barcarolle": { "composer": "Jacques Offenbach", "title": "Barcarolle from 'The Tales of Hoffmann'", "keywords": ["offenbach", "hoffmann"], "duration": "03:04", "description": "The 'Barcarolle' is the most famous melody from Jacques Offenbach's opera 'The Tales of Hoffmann.' It is a beautiful duet with a gentle, rocking rhythm meant to evoke the feeling of being in a Venetian gondola at night. The music is renowned for its enchanting and slightly melancholic beauty. The lyrical, interwoven melodies make it a perfect piece for a violin transcription, requiring a sweet tone and a graceful, flowing bow arm.", "usualTempo": 80, "practiceTempo": 66 },
    "bridge_gondoliera": { "composer": "Frank Bridge", "title": "Gondoliera, H. 80", "keywords": ["bridge", "gondola"], "duration": "04:24", "description": "'Gondoliera' is a charming character piece for violin and piano by the English composer Frank Bridge. Like other barcarolles, it evokes the gentle, rocking motion of a Venetian gondola. The piece features a beautiful, lyrical melody that requires a sweet, singing tone from the violinist. Bridge's sophisticated harmonies add a layer of richness and emotional depth to the simple, evocative scene he paints.", "usualTempo": 76, "practiceTempo": 60 },
    "massenet_meditation": { "composer": "Jules Massenet", "title": "Méditation from 'Thaïs'", "keywords": ["massenet", "thais"], "duration": "04:53", "description": "The 'Méditation' is a symphonic intermezzo from the opera 'Thaïs' and has become one of the most beloved pieces in the violin repertoire. It occurs between the acts as the courtesan Thaïs reflects and decides to change her life, representing her spiritual conversion. The music is intensely beautiful, with a soaring, lyrical melody that requires immense bow control and a pure, singing tone. It is a profound piece that demands both technical poise and deep emotional expression.", "usualTempo": 52, "practiceTempo": 42 },
    "part_spiegel_im_spiegel": { "composer": "Arvo Pärt", "title": "Spiegel im Spiegel", "keywords": ["pärt", "minimalist"], "duration": "08:30", "description": "'Spiegel im Spiegel,' meaning 'Mirror in the Mirror,' is a seminal work of minimalist music by the Estonian composer Arvo Pärt. The piece is characterized by its extreme simplicity, slow tempo, and meditative quality. It consists of a simple, arpeggiated piano part and a slow, lyrical violin melody that unfolds with a sense of timeless calm. Performing this piece requires incredible control, a pure tone, and the ability to sustain a long, unbroken musical line, creating a profoundly peaceful and introspective atmosphere.", "usualTempo": 40, "practiceTempo": 30 },
    "brahms_wiegenlied": { "composer": "Johannes Brahms", "title": "Wiegenlied (Brahms's Lullaby), Op. 49, No. 4", "keywords": ["brahms", "lullaby"], "duration": "02:08", "description": "Commonly known as 'Brahms's Lullaby,' 'Wiegenlied' is one of the most famous melodies ever written. Composed to celebrate the birth of a friend's son, its gentle, rocking rhythm and simple, comforting melody have made it a universal song of peace. While originally a song for voice and piano, it is frequently arranged for various instruments. On the violin or string orchestra, the piece requires a warm, gentle tone and a smooth bowing technique to convey its sense of tender affection.", "usualTempo": 76, "practiceTempo": 63 },
    "schubert_ave_maria": { "composer": "Franz Schubert", "title": "Ave Maria, D. 839", "keywords": ["schubert"], "duration": "05:00", "description": "While often used in religious services, Schubert's 'Ave Maria' was originally a song setting from Sir Walter Scott's poem 'The Lady of the Lake.' It is one of the composer's most famous works, beloved for its beautiful, serene melody and the sense of peace it conveys. The piece unfolds as a prayer, with a flowing accompaniment supporting a lyrical and devotional vocal line. Violin arrangements capture the song's purity and require a beautiful, singing tone and expressive phrasing.", "usualTempo": 50, "practiceTempo": 40 },
    "schubert_standchen": { "composer": "Franz Schubert", "title": "Ständchen (Serenade), D. 957", "keywords": ["schubert", "serenade"], "duration": "04:10", "description": "From the song cycle 'Schwanengesang' (Swan Song), 'Ständchen' is one of Schubert's most famous and beloved melodies. The piece is a serenade, with the piano accompaniment imitating the gentle strumming of a guitar. The vocal line, often transcribed for violin, is a beautiful and yearning plea to a loved one. It requires a deeply expressive and lyrical approach to capture its romantic and slightly melancholic character.", "usualTempo": 66, "practiceTempo": 54 },
    "puccini_o_mio_babbino_caro": { "composer": "Giacomo Puccini", "title": "O Mio Babbino Caro", "keywords": ["puccini", "gianni schicchi"], "duration": "02:47", "description": "From the opera 'Gianni Schicchi,' this is one of the most famous and beloved soprano arias in the entire operatic repertoire. In the story, the character Lauretta sings this plea to her father ('O My Dear Papa') to allow her to be with the man she loves. The music is incredibly lyrical, emotional, and builds to a beautiful, soaring climax. Violin and string orchestra arrangements are very popular, as they perfectly capture the aria's intense passion and melodic beauty.", "usualTempo": 88, "practiceTempo": 70 },
    "grieg_morning_mood": { "composer": "Edvard Grieg", "title": "Peer Gynt Suite No. 1: Morning Mood", "keywords": ["grieg", "peer gynt"], "duration": "03:21", "description": "This iconic piece is the opening movement of the 'Peer Gynt Suite No. 1' and famously depicts a sunrise in the Moroccan desert. The music begins gently with a simple, pastoral melody played by the flute, gradually building in texture and volume as more instruments join. This crescendo perfectly evokes the rising sun and the awakening of nature. It is one of the most recognizable pieces in classical music, celebrated for its beautiful orchestration and evocative atmosphere.", "usualTempo": 72, "practiceTempo": 60 },
    "hoffman_serenade": { "composer": "Peter Hoffman (attr. Roman Hoffstetter)", "title": "String Quartet in F Major, Op. 3 No. 5: II. Serenade", "keywords": ["hoffman", "haydn", "serenade"], "duration": "03:05", "description": "Long attributed to Joseph Haydn, this famous Serenade is now believed to have been composed by Roman Hoffstetter. It is the second movement of a string quartet and has become a standalone favorite. The piece features a beautiful, lyrical melody played by the first violin over a gentle pizzicato accompaniment from the other strings. It requires a sweet, singing tone and an elegant sense of phrasing to capture its graceful and charming character.", "usualTempo": 63, "practiceTempo": 52 },
    "boccherini_minuetto": { "composer": "Luigi Boccherini", "title": "String Quintet in E Major, G. 275: III. Minuetto", "keywords": ["boccherini", "minuet"], "duration": "04:00", "description": "This famous Minuet is the third movement from one of Luigi Boccherini's string quintets. It has become so popular that it is often performed as a standalone piece and is a staple of the classical repertoire. The music is the epitome of classical elegance and charm, with a graceful, stately character. It requires a light, clean touch and precise articulation to capture its courtly dance feel. The piece is beloved for its memorable melody and refined, galant style.", "usualTempo": 116, "practiceTempo": 92 },
    "vivaldi_spring_1": { "composer": "Antonio Vivaldi", "title": "The Four Seasons, Spring: I. Allegro", "keywords": ["vivaldi", "spring", "allegro"], "duration": "03:15", "description": "The opening movement of 'Spring' joyfully announces the arrival of the season. Vivaldi uses brilliant string textures to imitate birdsong and bubbling brooks. The music is energetic and celebratory, with the solo violin leading the orchestra in a vibrant dance. It is a quintessential example of Baroque programmatic music, painting a vivid picture of nature's awakening. The piece requires crisp articulation and a light, agile technique.", "usualTempo": 100, "practiceTempo": 80 },
    "vivaldi_spring_2": { "composer": "Antonio Vivaldi", "title": "The Four Seasons, Spring: II. Largo", "keywords": ["vivaldi", "spring", "largo"], "duration": "02:22", "description": "The slow movement of 'Spring' depicts a sleeping goatherd, with the solo violin's gentle melody representing his peaceful dreams. The violas in the orchestra softly imitate the rustling of leaves, while the cellos provide a gentle, rhythmic pulse. This movement is a beautiful example of Vivaldi's ability to create a serene and atmospheric scene. It requires a beautiful, sustained tone and a delicate touch from the soloist.", "usualTempo": 50, "practiceTempo": 40 },
    "vivaldi_spring_3": { "composer": "Antonio Vivaldi", "title": "The Four Seasons, Spring: III. Allegro pastorale", "keywords": ["vivaldi", "spring", "pastorale"], "duration": "03:45", "description": "The finale of 'Spring' is a lively pastoral dance, celebrating the arrival of the season with nymphs and shepherds. The music is rustic and joyful, with a drone-like accompaniment in the lower strings that evokes the sound of a bagpipe. The solo violin and orchestra engage in a playful and energetic dialogue. This movement requires a lively bowing style and rhythmic vitality to capture its festive and rustic character.", "usualTempo": 116, "practiceTempo": 92 },
    "vivaldi_summer_1": { "composer": "Antonio Vivaldi", "title": "The Four Seasons, Summer: I. Allegro non molto", "keywords": ["vivaldi", "summer", "allegro"], "duration": "05:06", "description": "The first movement of 'Summer' depicts a languid, sweltering heat, with the music conveying a sense of weariness. This calm is interrupted by the calls of the cuckoo and turtledove, represented by the solo violin. The movement builds in intensity, culminating in a musical depiction of a gathering storm. It showcases Vivaldi's mastery of dramatic contrast, from oppressive heat to the violent fury of the elements.", "usualTempo": 92, "practiceTempo": 74 },
    "vivaldi_summer_2": { "composer": "Antonio Vivaldi", "title": "The Four Seasons, Summer: II. Adagio", "keywords": ["vivaldi", "summer", "adagio"], "duration": "02:05", "description": "The short Adagio of 'Summer' portrays a shepherd's fear of the impending storm. The solo violin's anxious melody represents the shepherd, while the rumbling in the lower strings depicts the distant thunder. The movement is filled with a sense of foreboding and tension. It serves as a dramatic bridge between the oppressive heat of the first movement and the violent storm of the finale.", "usualTempo": 54, "practiceTempo": 44 },
    "vivaldi_summer_3": { "composer": "Antonio Vivaldi", "title": "The Four Seasons, Summer: III. Presto", "keywords": ["vivaldi", "summer", "presto"], "duration": "02:40", "description": "The finale of 'Summer' is a dramatic and virtuosic depiction of a violent summer storm. The music is fast and furious, with the solo violin playing rapid scales and arpeggios that represent the driving rain and flashes of lightning. The orchestra provides a powerful and turbulent accompaniment, depicting the roaring thunder. This movement is a thrilling showcase of Baroque virtuosity and dramatic storytelling.", "usualTempo": 132, "practiceTempo": 105 },
    "vivaldi_autumn_1": { "composer": "Antonio Vivaldi", "title": "The Four Seasons, Autumn: I. Allegro", "keywords": ["vivaldi", "autumn", "allegro"], "duration": "04:51", "description": "The first movement of 'Autumn' depicts a peasant harvest festival. The music is joyful and rustic, with a dance-like rhythm that celebrates the successful harvest. Vivaldi cleverly portrays the villagers becoming increasingly inebriated, with the music becoming more boisterous and a little clumsy. The movement is a cheerful and lively celebration of country life, filled with Vivaldi's characteristic energy and charm.", "usualTempo": 112, "practiceTempo": 90 },
    "vivaldi_autumn_2": { "composer": "Antonio Vivaldi", "title": "The Four Seasons, Autumn: II. Adagio Molto", "keywords": ["vivaldi", "autumn", "adagio"], "duration": "02:20", "description": "After the lively harvest festival, the second movement of 'Autumn' depicts the villagers' peaceful sleep. The music is slow, serene, and beautiful, with a gentle, muted string texture. The harpsichord plays a quiet, arpeggiated part, adding to the tranquil atmosphere. This movement is a moment of calm and repose, showcasing Vivaldi's ability to create a sense of deep peace and stillness.", "usualTempo": 48, "practiceTempo": 38 },
    "vivaldi_autumn_3": { "composer": "Antonio Vivaldi", "title": "The Four Seasons, Autumn: III. Allegro", "keywords": ["vivaldi", "autumn", "allegro"], "duration": "03:16", "description": "The finale of 'Autumn' is a vivid depiction of a hunt. The music is fast and energetic, with fanfares and galloping rhythms that evoke the excitement of the chase. The solo violin represents the fleeing animal, with virtuosic passages that depict its desperate attempts to escape. The orchestra represents the hunters, with powerful and driving rhythms. This movement is another brilliant example of Vivaldi's programmatic writing.", "usualTempo": 120, "practiceTempo": 96 },
    "vivaldi_winter_1": { "composer": "Antonio Vivaldi", "title": "The Four Seasons, Winter: I. Allegro non molto", "keywords": ["vivaldi", "winter", "allegro"], "duration": "03:16", "description": "The opening of 'Winter' is a stark and dramatic depiction of a frozen landscape. The music begins with shivering strings and dissonant harmonies that evoke the biting cold. The solo violin enters with fast, virtuosic passages that represent the chattering of teeth and the stamping of feet to keep warm. Vivaldi masterfully creates a sense of icy desolation and the harshness of winter in this powerful movement.", "usualTempo": 92, "practiceTempo": 74 },
    "vivaldi_winter_2_largo": { "composer": "Antonio Vivaldi", "title": "The Four Seasons, Winter: II. Largo", "keywords": ["vivaldi", "winter", "largo"], "duration": "01:57", "description": "The second movement of 'Winter' provides a stark contrast to the icy first movement. It depicts the cozy warmth of sitting by a fire while rain drips outside. The solo violin plays a beautiful, serene melody over the gentle pizzicato (plucked) strings of the orchestra, which represent the falling rain. This movement is a masterpiece of texture and atmosphere, requiring a beautiful, singing tone and excellent bow control from the soloist.", "usualTempo": 45, "practiceTempo": 35 },
    "vivaldi_winter_3": { "composer": "Antonio Vivaldi", "title": "The Four Seasons, Winter: III. Allegro", "keywords": ["vivaldi", "winter", "allegro"], "duration": "03:06", "description": "The finale of 'Winter' depicts the joy of moving about on the ice. The music begins with a depiction of slipping and sliding, with the solo violin playing rapid and virtuosic passages. The movement then shifts to a more dramatic section, representing the cracking of the ice and the fury of a winter storm. It concludes with a sense of triumph, as winter, for all its harshness, also brings its own kind of joy.", "usualTempo": 108, "practiceTempo": 86 },
    "piazzolla_vuelvo_al_sur": { "composer": "Astor Piazzolla", "title": "Vuelvo al Sur", "keywords": ["piazzolla", "sur"], "duration": "04:10", "description": "'Vuelvo al Sur' (I'm Returning to the South) is a beautiful and nostalgic tango by Astor Piazzolla. The piece expresses a deep sense of longing and a desire to return home. The music is more lyrical and melancholic than some of Piazzolla's more fiery tangos. It features a beautiful, soaring melody that requires a rich, expressive tone and a deep understanding of the flexible tango rhythm.", "usualTempo": 88, "practiceTempo": 70 },
    "mendelssohn_double_concerto_1": { "composer": "Felix Mendelssohn", "title": "Double Concerto in D minor: I. Allegro", "keywords": ["mendelssohn", "double"], "duration": "18:04", "description": "Written when he was only 14, Mendelssohn's Double Concerto for Violin and Piano is a remarkable achievement. The first movement, Allegro, is expansive and dramatic, filled with youthful energy and passion. It features brilliant and virtuosic writing for both soloists, who engage in a spirited dialogue. The movement showcases Mendelssohn's early mastery of form and his gift for creating memorable, soaring melodies within the classical tradition.", "usualTempo": 120, "practiceTempo": 96 },
    "mendelssohn_double_concerto_2": { "composer": "Felix Mendelssohn", "title": "Double Concerto in D minor: II. Adagio", "keywords": ["mendelssohn", "double"], "duration": "10:16", "description": "The second movement of Mendelssohn's Double Concerto is a beautiful and lyrical Adagio. It provides a moment of calm and introspection between the fiery outer movements. The violin and piano trade a beautiful, song-like melody over a gentle string accompaniment. This movement requires a beautiful, singing tone and a deep sense of musical phrasing from both soloists to convey its sense of peaceful serenity.", "usualTempo": 60, "practiceTempo": 50 },
    "mendelssohn_double_concerto_3": { "composer": "Felix Mendelssohn", "title": "Double Concerto in D minor: III. Allegro molto", "keywords": ["mendelssohn", "double"], "duration": "06:29", "description": "The finale of Mendelssohn's Double Concerto is a brilliant and energetic Allegro molto. It is a virtuosic showcase for both the violin and piano, filled with rapid passagework and a sense of joyful exuberance. The movement has a gypsy-like character, with a fiery and rhythmic main theme. It brings the concerto to a thrilling and exciting conclusion, demonstrating the young composer's incredible technical skill and musical imagination.", "usualTempo": 132, "practiceTempo": 105 },
    "mozart_violin_concerto_5_1_allegro": { "composer": "Wolfgang Amadeus Mozart", "title": "Violin Concerto No. 5, K. 219: I. Allegro aperto", "keywords": ["mozart", "turkish", "allegro"], "duration": "10:09", "description": "The first movement of Mozart's 'Turkish' concerto begins with a graceful orchestral introduction before the violin makes a surprise, ethereal Adagio entrance. The main Allegro section is elegant and brilliant, showcasing the violin's virtuosity with rapid scales and arpeggios. The movement is a perfect example of Mozart's classical clarity, formal balance, and operatic grace. It demands a clean, precise technique and a sophisticated understanding of style.", "usualTempo": 112, "practiceTempo": 90 },
    "mozart_violin_concerto_5_2": { "composer": "Wolfgang Amadeus Mozart", "title": "Violin Concerto No. 5, K. 219: II. Adagio", "keywords": ["mozart", "turkish", "adagio"], "duration": "11:55", "description": "The second movement of Mozart's Fifth Violin Concerto is a beautiful and serene Adagio. It is a moment of pure lyrical beauty, with the solo violin spinning out a long, graceful melody over a gentle orchestral accompaniment. This movement is a test of the violinist's ability to produce a beautiful, singing tone and to shape phrases with elegance and sensitivity. It is a masterpiece of classical expression, conveying a sense of calm and profound beauty.", "usualTempo": 60, "practiceTempo": 50 },
    "mozart_violin_concerto_5_3": { "composer": "Wolfgang Amadeus Mozart", "title": "Violin Concerto No. 5, K. 219: III. Tempo di minuetto", "keywords": ["mozart", "turkish", "minuetto"], "duration": "09:17", "description": "The finale of Mozart's Fifth Violin Concerto is a graceful Tempo di Minuetto. However, the movement is famous for its surprising middle section, a boisterous and exotic-sounding 'Turkish' episode that gives the concerto its nickname. This section features crashing cymbals and a fiery, percussive character that was fashionable at the time. The movement is a brilliant and playful conclusion to the concerto, showcasing Mozart's wit and imagination.", "usualTempo": 120, "practiceTempo": 96 },
    "tartini_adagio": { "composer": "Giuseppe Tartini", "title": "Adagio for Violin and Strings", "keywords": ["tartini"], "duration": "03:39", "description": "Giuseppe Tartini was a master of the Baroque violin, and this Adagio is a beautiful example of his lyrical and expressive style. The piece features a slow, beautiful melody that unfolds over a simple string accompaniment. It is a work of great emotional depth and requires a beautiful, singing tone and a deep understanding of Baroque ornamentation and phrasing. This Adagio is a testament to Tartini's ability to write music of profound beauty and emotional power.", "usualTempo": 52, "practiceTempo": 42 },
    "brahms_violin_concerto_1": { "composer": "Johannes Brahms", "title": "Violin Concerto in D Major, Op. 77: I. Allegro non troppo", "keywords": ["brahms", "concerto", "allegro"], "duration": "23:18", "description": "The first movement of Brahms's Violin Concerto is a monumental work, symphonic in scope. It is known for its rich harmonies, complex structure, and the beautiful integration of the solo violin with the orchestra. The movement is heroic and majestic, with a powerful and sweeping main theme. It demands immense technical skill and profound musical maturity from the soloist, making it a cornerstone of the violin repertoire.", "usualTempo": 96, "practiceTempo": 76 },
    "brahms_violin_concerto_2": { "composer": "Johannes Brahms", "title": "Violin Concerto in D Major, Op. 77: II. Adagio", "keywords": ["brahms", "concerto", "adagio"], "duration": "09:16", "description": "The second movement of Brahms's Violin Concerto is a deeply expressive and beautiful Adagio. It is one of the most sublime slow movements in the entire violin repertoire. The main theme, introduced by the oboe, is a beautiful and serene melody that is then taken up and embellished by the solo violin. This movement requires a beautiful, singing tone and a profound sense of musical phrasing to convey its sense of peace and deep emotion.", "usualTempo": 58, "practiceTempo": 48 },
    "brahms_violin_concerto_3": { "composer": "Johannes Brahms", "title": "Violin Concerto in D Major, Op. 77: III. Allegro giocoso", "keywords": ["brahms", "concerto", "giocoso"], "duration": "08:33", "description": "The finale of Brahms's Violin Concerto is a fiery and energetic Allegro giocoso, heavily influenced by Hungarian folk music. The movement is a brilliant and virtuosic showcase for the solo violin, with a driving, dance-like rhythm and a sense of joyful exuberance. It brings the concerto to a thrilling and triumphant conclusion. This movement demands a high level of technical proficiency and a bold, spirited character from the soloist.", "usualTempo": 120, "practiceTempo": 96 },
    "tchaikovsky_violin_concerto_1": { "composer": "Pyotr Ilyich Tchaikovsky", "title": "Violin Concerto, Op. 35: I. Allegro moderato", "keywords": ["tchaikovsky", "concerto", "allegro"], "duration": "19:26", "description": "The first movement of Tchaikovsky's Violin Concerto is one of the most famous and beloved in the repertoire. It is a work of immense passion and drama, filled with beautiful Russian melodies and dazzling virtuosic passages. The movement is expansive and sweeping, with a powerful and memorable main theme. It is a true test of a violinist's technical and expressive abilities, demanding both brilliant virtuosity and deep musical sensitivity.", "usualTempo": 120, "practiceTempo": 92 },
    "tchaikovsky_violin_concerto_2": { "composer": "Pyotr Ilyich Tchaikovsky", "title": "Violin Concerto, Op. 35: II. Canzonetta", "keywords": ["tchaikovsky", "concerto", "canzonetta"], "duration": "07:05", "description": "The second movement, titled 'Canzonetta' (little song), provides a moment of lyrical and melancholic calm between the fiery outer movements. It is a beautiful and introspective piece, with a simple, song-like melody that has a distinctively Russian character. This movement requires a beautiful, singing tone and a deep sense of musical phrasing to convey its sense of gentle sadness and nostalgia. It serves as a beautiful interlude before the thrilling finale.", "usualTempo": 72, "practiceTempo": 58 },
    "tchaikovsky_violin_concerto_3": { "composer": "Pyotr Ilyich Tchaikovsky", "title": "Violin Concerto, Op. 35: III. Finale. Allegro Vivacissimo", "keywords": ["tchaikovsky", "concerto", "finale"], "duration": "10:39", "description": "The finale of Tchaikovsky's Violin Concerto is a thrilling and energetic Allegro Vivacissimo. It is heavily influenced by Russian folk dance music, with a fiery and rhythmic main theme. The movement is a brilliant and virtuosic showcase for the solo violin, with rapid passagework and a sense of joyful abandon. It brings the concerto to a triumphant and exhilarating conclusion, leaving the audience breathless.", "usualTempo": 160, "practiceTempo": 128 },
    "mendelssohn_violin_concerto_1": { "composer": "Felix Mendelssohn", "title": "Violin Concerto, Op. 64: I. Allegro molto appassionato", "keywords": ["mendelssohn", "concerto", "allegro"], "duration": "13:54", "description": "The first movement of Mendelssohn's Violin Concerto is a masterpiece of the Romantic era. It begins with the solo violin immediately stating the soaring and passionate main theme. The movement is filled with brilliant and virtuosic writing for the soloist, including a famous and challenging cadenza. It is celebrated for its structural innovations, its beautiful melodies, and its sense of emotional urgency and drama.", "usualTempo": 126, "practiceTempo": 100 },
    "mendelssohn_violin_concerto_2": { "composer": "Felix Mendelssohn", "title": "Violin Concerto, Op. 64: II. Andante", "keywords": ["mendelssohn", "concerto", "andante"], "duration": "08:30", "description": "The second movement of Mendelssohn's Violin Concerto is a beautiful and serene Andante. It is a simple and lyrical song without words, providing a moment of calm and introspection. The solo violin spins out a long, graceful melody over a gentle orchestral accompaniment. This movement requires a beautiful, singing tone and a deep sense of musical phrasing to convey its sense of peace and gentle melancholy.", "usualTempo": 76, "practiceTempo": 60 },
    "mendelssohn_violin_concerto_3": { "composer": "Felix Mendelssohn", "title": "Violin Concerto, Op. 64: III. Allegro molto vivace", "keywords": ["mendelssohn", "concerto", "vivace"], "duration": "06:50", "description": "The finale of Mendelssohn's Violin Concerto is a light, sparkling, and virtuosic Allegro molto vivace. It has a scherzo-like character, with a sense of playful energy and elfin grace that is characteristic of Mendelssohn's style. The movement is a brilliant showcase for the soloist's agility and technical skill, with rapid passagework and a light, crisp bowing style. It brings the concerto to a joyful and exhilarating conclusion.", "usualTempo": 168, "practiceTempo": 134 },
}

# --- HELPER FUNCTIONS --- (Unchanged)
def fetch_piece_info(piece_name):
    if not piece_name: return None
    search_terms = piece_name.lower().split()
    for key, piece in pieceDatabase.items():
        searchable_text = f"{piece['title'].lower()} {piece['composer'].lower()} {' '.join(piece['keywords'])}"
        if all(term in searchable_text for term in search_terms):
            return piece
    return {"title": piece_name, "description": f"Information for '{piece_name}' could not be found.", "composer": "Unknown", "notFound": True}

def analyze_audio_features(audio_bytes):
    if not audio_bytes: return None
    try:
        sound = AudioSegment.from_file(io.BytesIO(audio_bytes))
        sound = sound.set_channels(1) # Mono for consistent analysis
        audio_array = np.array(sound.get_array_of_samples())
        framerate = sound.frame_rate
        normalized_audio = audio_array / (2**(sound.sample_width * 8 - 1))
        duration = len(normalized_audio) / framerate
        avg_amplitude = np.mean(np.abs(normalized_audio))
        peak_amplitude = np.max(np.abs(normalized_audio))
        return {
            "waveform": normalized_audio, "framerate": framerate, "duration": duration,
            "avg_amplitude": avg_amplitude, "peak_amplitude": peak_amplitude
        }
    except Exception as e:
        st.error(f"Could not process audio file. It might be corrupted. Error: {e}")
        return None

def get_human_comparative_analysis(benchmark_features, user_features):
    if not benchmark_features or not user_features: return "Could not analyze one or both audio files."
    dyn_comp = "very similar to"
    if user_features["avg_amplitude"] > benchmark_features["avg_amplitude"] * 1.15: dyn_comp = "generally louder and more powerful than"
    elif user_features["avg_amplitude"] < benchmark_features["avg_amplitude"] * 0.85: dyn_comp = "quieter and more reserved than"
    duration_ratio = user_features["duration"] / benchmark_features["duration"]
    tempo_comp = "at a very similar tempo to"
    if duration_ratio < 0.95: tempo_comp = "significantly faster than"
    elif duration_ratio > 1.05: tempo_comp = "significantly slower than"
    return (f"**Tempo:** You played this piece **{tempo_comp}** the benchmark, taking {user_features['duration']:.1f} seconds compared to the benchmark's {benchmark_features['duration']:.1f} seconds.\n\n"
            f"**Dynamics:** Your performance was **{dyn_comp}** the benchmark. This is reflected in the average loudness of your recording ({user_features['avg_amplitude']:.2f}) versus the goal ({benchmark_features['avg_amplitude']:.2f}).\n\n"
            f"**Tonal Quality:** Based on the waveforms, your peak amplitudes are {'higher' if user_features['peak_amplitude'] > benchmark_features['peak_amplitude'] else 'lower'} than the benchmark, suggesting a difference in attack and bow pressure.")

def plot_waveform(features, title, color):
    fig, ax = plt.subplots(figsize=(10, 2))
    time_axis = np.linspace(0, features["duration"], num=len(features["waveform"]))
    ax.plot(time_axis, features["waveform"], color=color, linewidth=0.5)
    ax.set_title(title, color='white'); ax.set_xlabel("Time (s)", color='white')
    ax.set_ylabel("Amplitude", color='white'); ax.set_ylim([-1, 1])
    ax.grid(True, alpha=0.2, color='#888888'); ax.tick_params(colors='white', which='both')
    fig.patch.set_facecolor('none'); ax.set_facecolor('none')
    return fig

# --- STATE INITIALIZATION & HELPERS ---
def init_state():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.search_query = ''; st.session_state.searched_piece_info = None
        st.session_state.user_audio_bytes = None
        st.session_state.benchmark_audio_bytes = None; st.session_state.ai_feedback = ""
        st.session_state.analysis_error = ''; st.session_state.analysis_complete = False
        st.session_state.benchmark_history = []; st.session_state.user_history = []
        st.session_state.audio_frames = []; st.session_state.volume_level = 0.0

def add_to_history(history_key, audio_bytes, source_name):
    history = st.session_state[history_key]
    timestamp = datetime.now().strftime("%H:%M:%S")
    history.insert(0, {"timestamp": timestamp, "audio": audio_bytes, "name": source_name})
    st.session_state[history_key] = history[:5]

def create_audio_input_section(title, type_key):
    st.subheader(title)
    with st.expander(f"Upload an Audio File"):
        uploaded_file = st.file_uploader(f"Upload {type_key.capitalize()} Audio", type=['wav', 'mp3', 'm4a'], key=f"{type_key}_uploader")
        if uploaded_file:
            audio_bytes = uploaded_file.getvalue()
            if audio_bytes != st.session_state.get(f"{type_key}_audio_bytes"):
                st.session_state[f"{type_key}_audio_bytes"] = audio_bytes
                add_to_history(f"{type_key}_history", audio_bytes, uploaded_file.name)
                st.rerun()
    with st.expander(f"Record Live Audio"):
        webrtc_ctx = webrtc_streamer(key=f"{type_key}_recorder", mode=WebRtcMode.SENDONLY, audio_frame_callback=audio_frame_callback, media_stream_constraints={"audio": True, "video": False})
        if webrtc_ctx.state.playing:
            st.progress(st.session_state.get("volume_level", 0), text=f"Recording... {st.session_state.get('volume_level', 0)}%")
        if not webrtc_ctx.state.playing and len(st.session_state.get("audio_frames", [])) > 0:
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wf:
                wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(48000)
                wf.writeframes(b''.join(st.session_state.audio_frames))
            st.session_state[f"{type_key}_audio_bytes"] = wav_buffer.getvalue()
            st.session_state.audio_frames = [] # Clear buffer
            add_to_history(f"{type_key}_history", st.session_state[f"{type_key}_audio_bytes"], "Live Recording")
            st.rerun()
    if st.session_state.get(f"{type_key}_audio_bytes"):
        st.write(f"**Current {type_key.capitalize()}:**")
        st.audio(st.session_state[f"{type_key}_audio_bytes"])
    if st.session_state.get(f"{type_key}_history"):
        with st.expander("View History (Last 5)"):
            for record in st.session_state[f"{type_key}_history"]:
                st.write(f"{record['name']} ({record['timestamp']})")
                st.audio(record['audio'])

# --- MAIN APP LAYOUT ---
st.set_page_config(layout="centered", page_title="Violin Studio")
init_state()

st.markdown("""
    <style>
        .stApp { background-color: #000000; }
        #MainMenu, footer { visibility: hidden; }
        h1 a, h2 a, h3 a { display: none !important; }
        div[role="tablist"] { justify-content: center; }
        button[role="tab"] { font-size: 1.2rem; padding: 10px 20px; border: 2px solid transparent; }
        button[role="tab"][aria-selected="true"] { border-bottom: 2px solid #FFFF00; color: #FFFF00; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: yellow;'>Violin Studio</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["About the Piece", "Compare with Benchmark"])

with tab1:
    st.header("Musical Repertoire Explorer")
    search_query = st.text_input("Search for a piece:", placeholder="e.g., Vivaldi Four Seasons")
    if st.button("Search", key="search_piece"):
        st.session_state.searched_piece_info = fetch_piece_info(search_query)
    if st.session_state.searched_piece_info:
        info = st.session_state.searched_piece_info
        st.divider()
        st.subheader(info['title'])
        st.caption(f"By {info['composer']}")

with tab2:
    st.header("Compare with Benchmark")
    st.write("Provide a goal recording and your own performance, then get a direct comparison.")
    c1, c2 = st.columns(2)
    with c1:
        create_audio_input_section("Recording Goal", "benchmark")
    with c2:
        create_audio_input_section("My Recording", "user")

    st.divider()

    if st.session_state.benchmark_audio_bytes and st.session_state.user_audio_bytes:
        if st.button("Compare Recordings", type="primary", use_container_width=True):
            st.session_state.ai_feedback, st.session_state.analysis_error = "", ""
            with st.spinner("AI is analyzing your performance... This may take a moment."):
                benchmark_features = analyze_audio_features(st.session_state.benchmark_audio_bytes)
                user_features = analyze_audio_features(st.session_state.user_audio_bytes)
                time.sleep(2)
                if benchmark_features and user_features: 
                    st.session_state.ai_feedback = get_human_comparative_analysis(benchmark_features, user_features)
                else: 
                    st.session_state.analysis_error = "Could not process one or both audio files."
            st.session_state.analysis_complete = True
            st.rerun()
    
    if st.session_state.analysis_complete:
        st.toast("✅ Analysis Complete!")
        st.markdown("""
            <a href="#analysis-section" style="text-decoration: none;">
                <button style="background-color: #FFFF00; color: black; border: none; padding: 10px 20px; border-radius: 50px; font-weight: bold; cursor: pointer; width: 100%;">
                    View Analysis Results
                </button>
            </a>
        """, unsafe_allow_html=True)
    
    if st.session_state.ai_feedback or st.session_state.analysis_error:
        st.subheader("Comparative Analysis", anchor="analysis-section")
        if st.session_state.analysis_error: st.error(st.session_state.analysis_error)
        if st.session_state.ai_feedback:
            benchmark_features = analyze_audio_features(st.session_state.benchmark_audio_bytes)
            user_features = analyze_audio_features(st.session_state.user_audio_bytes)
            if benchmark_features and user_features:
                c1, c2 = st.columns(2)
                c1.pyplot(plot_waveform(benchmark_features, "Benchmark Waveform", "#FFFF00"))
                c2.pyplot(plot_waveform(user_features, "Your Waveform", "#FFFFFF"))
            st.markdown(st.session_state.ai_feedback)
