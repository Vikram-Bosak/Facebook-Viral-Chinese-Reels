import os
import re
from openai import OpenAI
import json
try:
    from .logger import logger
except ImportError:
    from logger import logger

def clean_filename(filename):
    # Remove extension and replace underscores/hyphens with spaces
    name_without_ext = os.path.splitext(filename)[0]
    cleaned = re.sub(r'[-_]', ' ', name_without_ext)
    return cleaned.strip()

def generate_seo_metadata(filename, media_type='reel'):
    """
    Generates SEO title, description, and hashtags based on the video filename.
    Returns a dictionary with 'title', 'description', and 'hashtags'.
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        logger.warning("OPENAI_API_KEY not found. Using fallback metadata generator.")
        return generate_fallback_metadata(filename)
        
    base_url = os.environ.get('OPENAI_API_BASE_URL')
    model = os.environ.get('OPENAI_API_MODEL', 'gpt-3.5-turbo')
    
    if base_url:
        client = OpenAI(api_key=api_key, base_url=base_url)
    else:
        client = OpenAI(api_key=api_key)
        
    topic = clean_filename(filename)
    
    content_type_str = "Chinese Facebook Reel" if media_type == 'reel' else "Chinese Facebook Photo Post"
    video_str = "short vertical video (Facebook Reel / YouTube Shorts)" if media_type == 'reel' else "stunning photo/image"
    hashtag_str = "#Reels #短视频" if media_type == 'reel' else "#PhotoOfTheDay #短视频"
    
    system_prompt = (
        f"You are an expert Social Media Manager specializing in Chinese viral content for Facebook and YouTube Shorts targeting Chinese-speaking audiences. "
        "Your goal is to maximize engagement, click-through rate, and virality among Chinese-speaking viewers worldwide. "
        "All generated titles, descriptions, and hashtags must be in Chinese (中文) unless the topic is clearly English-focused."
    )
    
    user_prompt = f"""
    Generate viral SEO metadata for a {video_str} about: "{topic}".
    
    Requirements:
    1. Title (标题): Short, catchy, uses emotional words, includes relevant emojis. Written in Chinese (中文). Max 60 characters.
    2. Description (描述): 1-2 short sentences in Chinese that create curiosity and encourage engagement.
    3. Hashtags (标签): 5-8 highly relevant and trending hashtags. Mix Chinese trending tags with topic-specific tags. Include {hashtag_str}.
    
    Chinese Hashtag Guidelines:
    - Always include popular Chinese viral tags such as: #中国 #中国风 #抖音 #短视频 #热门 #推荐 #火了 #笑死我了 #涨知识 #治愈
    - Add topic-specific Chinese tags where relevant
    - Use both simplified Chinese hashtags and English viral hashtags for maximum reach
    
    Format the output exactly as JSON:
    {{
        "title": "...",
        "description": "...",
        "hashtags": "#tag1 #tag2 ..."
    }}
    """
    
    try:
        params = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7
        }
        if "gpt-" in model:
            params["response_format"] = {"type": "json_object"}
            
        response = client.chat.completions.create(**params)
        
        result_json = response.choices[0].message.content.strip()
        
        # Clean markdown code blocks if present
        if result_json.startswith("```"):
            result_json = re.sub(r'^```(?:json)?\n', '', result_json)
            result_json = re.sub(r'\n```$', '', result_json)
            result_json = result_json.strip()
            
        data = json.loads(result_json)
        
        return {
            'title': data.get('title', topic.title()),
            'description': data.get('description', f"精彩视频关于 {topic}！🔥"),
            'hashtags': data.get('hashtags', "#Reels #短视频 #热门 #viral #trending")
        }
        
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        return generate_fallback_metadata(filename)

def generate_fallback_metadata(filename):
    import hashlib
    
    def get_deterministic_choice(fn, lst):
        h = int(hashlib.md5(fn.encode('utf-8')).hexdigest(), 16)
        return lst[h % len(lst)]
        
    topic = clean_filename(filename)
    topic_title = topic.title()
    
    # Extract lowercase words for keyword matching
    words = [w.lower() for w in re.findall(r'\w+', topic) if len(w) > 2]
    
    # Define stopwords
    stopwords = {
        'the', 'and', 'for', 'you', 'with', 'from', 'this', 'that',
        'are', 'was', 'were', 'has', 'have', 'had', 'its', 'their', 'our',
        'your', 'his', 'her', 'she', 'him', 'them', 'who', 'whom', 'which'
    }
    
    keywords = [w for w in words if w not in stopwords]
    
    # Classify category
    wildlife_keywords = {
        'tiger', 'lion', 'leopard', 'cheetah', 'gorilla', 'elephant', 'shark', 'whale',
        'bear', 'eagle', 'hawk', 'snake', 'hunt', 'predator', 'safari', 'animal', 'wolf',
        'panther', 'jaguar', 'buffalo', 'crocodile', 'alligator'
    }
    
    nature_keywords = {
        'nature', 'forest', 'jungle', 'ocean', 'river', 'mountain', 'sea', 'sky',
        'rain', 'storm', 'scenic', 'landscape', 'valley', 'desert', 'beach', 'sunset',
        'sunrise', 'lake', 'waterfall', 'canyon'
    }
    
    chinese_culture_keywords = {
        'chinese', 'china', 'beijing', 'shanghai', 'temple', 'kungfu', 'martial',
        'dragon', 'lantern', 'tea', 'silk', 'wall', 'panda', 'dumpling', 'noodle',
        'dance', 'music', 'opera', 'calligraphy', 'painting', 'festival', 'newyear',
        'spring', 'autumn', 'ancient', 'traditional', 'culture', 'hanfu', 'cheongsam'
    }
    
    food_keywords = {
        'food', 'cooking', 'recipe', 'chef', 'kitchen', 'bake', 'grill', 'bbq',
        'noodle', 'dumpling', 'rice', 'wok', 'stir', 'soup', 'hotpot', 'dimsum',
        'sushi', 'ramen', 'fried', 'steamed', 'spicy', 'sweet'
    }
    
    is_wildlife = any(k in wildlife_keywords for k in keywords)
    is_nature = any(k in nature_keywords for k in keywords)
    is_chinese_culture = any(k in chinese_culture_keywords for k in keywords)
    is_food = any(k in food_keywords for k in keywords)
    
    # Common Chinese viral hashtags used across all categories
    common_chinese_tags = ['#中国', '#中国风', '#短视频', '#热门', '#推荐', '#火了', '#viral', '#trending']
    
    # Pre-saved SEO Patterns (Titles & Descriptions) - Chinese versions
    if is_wildlife:
        titles = [
            "太震撼了！{topic}的真面目！😱",
            "{topic}的力量简直不可思议！🔥",
            "POV：近距离目睹{topic}！🤯",
            "大自然最强大的猎手：{topic}！💪",
            "这段{topic}的视频让你目瞪口呆！🚨"
        ]
        descriptions = [
            "感受{topic}在野外的原始力量与美感。大自然永远让人惊叹！🌍",
            "近距离拍摄{topic}！难得一见的野生动物精彩瞬间。🐾",
            "这个{topic}的瞬间简直太不可思议了！绝对震撼！😱"
        ]
        cat_tags = ['#野生动物', '#大自然', '#动物世界', '#非洲', '#猎手', '#wildlifephotography', '#naturelovers', '#wild']
    elif is_nature:
        titles = [
            "绝美风景！{topic}的壮丽瞬间！🏔️",
            "{topic}的美简直令人窒息！✨",
            "大自然最美的画卷：{topic}！🌍",
            "沉浸在这震撼的{topic}美景中！🌿",
            "这个{topic}的景色太梦幻了！😍"
        ]
        descriptions = [
            "深呼吸，感受{topic}的壮丽风光与宁静。🍃",
            "这些{topic}的美景让你想立刻出发旅行！纯粹的美！✨",
            "大自然是最伟大的艺术家，{topic}就是一幅杰作！🌍"
        ]
        cat_tags = ['#风景', '#美景', '#自然风光', '#旅行', '#治愈', '#earth', '#travel', '#exploring']
    elif is_chinese_culture:
        titles = [
            "太惊艳了！{topic}的中国风！🐉",
            "这就是中华文化的魅力！{topic}！🏮",
            "传统之美：{topic}让你感受中国风！🎎",
            "太美了！{topic}的古典韵味！✨",
            "这个{topic}视频火遍全网！🔥"
        ]
        descriptions = [
            "感受{topic}的中国传统文化之美，东方魅力令人陶醉！🏮",
            "中华文化的博大精深，{topic}就是最好的证明！🐉",
            "这段{topic}的视频太惊艳了！传统文化就是这么有魅力！✨"
        ]
        cat_tags = ['#中国风', '#传统文化', '#中华文化', '#东方美学', '#古典', '#chineseculture', '#hanfu', '#traditional']
    elif is_food:
        titles = [
            "太香了！{topic}的做法绝了！🍜",
            "这个{topic}看饿了！🤤",
            "舌尖上的{topic}！中国传统美食！🥢",
            "你绝对没吃过这么正宗的{topic}！🔥",
            "这个{topic}视频太治愈了！😋"
        ]
        descriptions = [
            "看着这诱人的{topic}，口水都要流下来了！🥢",
            "中国传统美食的精髓：{topic}！每一口都是幸福！🍜",
            "这个{topic}的做法太绝了！收藏起来学着做！😋"
        ]
        cat_tags = ['#美食', '#中国美食', '#舌尖上的中国', '#家常菜', '#吃货', '#foodie', '#chinesefood', '#cooking']
    else:
        titles = [
            "太震撼了！{topic}的真面目！😱",
            "等一下！看到最后{topic}！🚨",
            "这个{topic}的视频太疯狂了！🤯",
            "快来看！{topic}！🎬",
            "这个{topic}的片段改变了我的认知！🔥"
        ]
        descriptions = [
            "这段{topic}的视频火爆全网！太震撼了！💥",
            "这个{topic}简直太不可思议了！必看视频！👇",
            "精彩的{topic}短视频！分享给需要看到的朋友！"
        ]
        cat_tags = ['#短视频', '#热门', '#推荐', '#涨知识', '#治愈', '#搞笑']
        
    # Get deterministic choices based on filename to keep output consistent per video
    title_template = get_deterministic_choice(filename, titles)
    desc_template = get_deterministic_choice(filename, descriptions)
    
    # Generate Title & Base Description
    title = title_template.format(topic=topic_title)
    # Ensure title length limit
    if len(title) > 60:
        title = title[:57] + "..."
        
    base_desc = desc_template.format(topic=topic_title)
    
    # Chinese CTAs (Call to Action)
    ctas = [
        "觉得有用就点赞收藏！❤️",
        "关注我，每天更新精彩内容！📲",
        "转发给需要看到的朋友！👇",
        "你怎么看？评论区告诉我！💬",
        "喜欢就分享出去吧！✈️",
        "双击屏幕给个赞！👍",
        "记得关注，不要错过更多精彩！🔔"
    ]
    cta = get_deterministic_choice(filename + "_cta", ctas)
    description = f"{base_desc}\n\n{cta}"
    
    # Keywords Database mapping (Chinese viral tags)
    KEYWORDS_DATABASE = {
        'tiger': ['老虎', '大猫', '猛兽', 'savethe-tigers'],
        'lion': ['狮子', '百兽之王', '大猫', 'wildlions'],
        'leopard': ['豹子', '花豹', '山中幽灵'],
        'cheetah': ['猎豹', '速度', '非洲草原'],
        'elephant': ['大象', '非洲象', 'gentlegiants'],
        'shark': ['鲨鱼', '海底世界', 'underwater'],
        'whale': ['鲸鱼', '大海', '海洋生物'],
        'gorilla': ['大猩猩', '灵长类', 'silverback'],
        'eagle': ['老鹰', '猛禽', '飞翔'],
        'hunt': ['狩猎', '捕食者', '生存'],
        'jungle': ['丛林', '热带雨林', '原始森林'],
        'mountain': ['山', '登山', '高山', '风景'],
        'ocean': ['大海', '海底', '海洋'],
        'panda': ['大熊猫', '国宝', '可爱'],
        'dragon': ['龙', '中国龙', '传统文化'],
        'tea': ['茶', '中国茶', '茶道'],
        'silk': ['丝绸', '丝绸之路', '传统工艺'],
        'dance': ['舞蹈', '中国舞', '古典舞'],
        'music': ['音乐', '中国风音乐', '古风'],
        'temple': ['寺庙', '古建筑', '中国古建筑'],
        'noodle': ['面条', '手工面', '中国面食'],
        'dumpling': ['饺子', '包子', '中国传统美食'],
        'hotpot': ['火锅', '麻辣火锅', '四川美食'],
        'cooking': ['做饭', '烹饪', '中国菜'],
        'food': ['美食', '好吃', '中国美食'],
        'spicy': ['辣', '麻辣', '川菜'],
        'fried': ['炒', '煎', '油炸'],
        'soup': ['汤', '煲汤', '养生汤'],
        'sweet': ['甜', '甜品', '中国甜点'],
        'spring': ['春天', '春季', '万物复苏'],
        'autumn': ['秋天', '秋色', '金秋'],
        'ancient': ['古代', '古风', '穿越'],
        'traditional': ['传统', '古典', '中国传统文化'],
        'festival': ['节日', '中国节', '传统节日'],
    }
    
    # Build Hashtags list
    # 1. Start with fundamental Chinese viral tags
    hash_tags_set = {'#短视频', '#热门', '#中国', '#中国风', '#viral', '#trending'}
    
    # 2. Add category tags
    for tag in cat_tags:
        hash_tags_set.add(tag.lower())
        
    # 3. Add tags from clean keywords database
    for k in keywords:
        if k in KEYWORDS_DATABASE:
            for extra in KEYWORDS_DATABASE[k]:
                hash_tags_set.add(f"#{extra}")
                
    # 4. Add keywords as tags themselves
    for k in keywords:
        if len(k) > 2:
            hash_tags_set.add(f"#{k}")
            
    # Convert set back to list, ensure we don't have duplicates, and limit to ~10 tags
    ordered_tags = ['#短视频', '#热门', '#中国', '#viral', '#trending']
    for tag in sorted(hash_tags_set):
        if tag not in ordered_tags:
            ordered_tags.append(tag)
            
    # Slice to a max of 10 hashtags to avoid tag stuffing
    final_tags = ordered_tags[:10]
    hashtags_str = " ".join(final_tags)
    
    return {
        'title': title,
        'description': description,
        'hashtags': hashtags_str
    }

def format_caption(seo_metadata):
    """
    Combines the title, description, and hashtags into the final Facebook caption format.
    """
    return f"{seo_metadata['title']}\n\n{seo_metadata['description']}\n\n{seo_metadata['hashtags']}"
