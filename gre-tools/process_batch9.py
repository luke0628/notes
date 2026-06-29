#!/usr/bin/env python3
"""Process GRE batch 9 raw data into structured JSONL output - 306 words taxing→tycoon."""
import json
import re

with open('/home/Lu/gre_batch_9_raw.json', 'r') as f:
    data = json.load(f)


def clean_parentheses(s):
    s = re.sub(r'[（(][^）)]*[）)]', '', s)
    s = re.sub(r'[\[][^\[\]]*[\]]', '', s)
    s = re.sub(r'[【][^】]*[】]', '', s)
    return s.strip('，,;: ')


# ── Root/structure knowledge base for GRE words ──
ROOT_MEMOS = {
    "taxing": "⭐词根：tax-税+ing→像交税一样负担重→繁重的",
    "tedious": "⭐词根：ted-厌倦+ious形容词后缀→令人厌倦的→冗长乏味的",
    "teeter": "⭐词根：teeter拟声词根，模仿摇摆不稳的声音→蹒跚，摇摆",
    "temerity": "⭐词根：temer-轻率+ity名词后缀→轻率，鲁莽",
    "temper": "⭐词根：temper-调和，原指木材的硬度调适→脾气，缓和",
    "temperament": "⭐词根：temper-调和+ament→人的性情调和方式→气质，性情",
    "temperate": "⭐词根：temper-节制+ate形容词后缀→有节制的，温和的",
    "tempestuous": "⭐词根：tempest-暴风雨+uous形容词后缀→暴风雨般的，狂暴的",
    "temporal": "⭐词根：tempor-时间+al形容词后缀→时间的，世俗的",
    "temporary": "⭐词根：tempor-时间+ary→一时的→暂时的，临时的",
    "tempt": "⭐词根：tempt-尝试→引诱尝试→诱惑，吸引",
    "tenacious": "⭐词根：ten-握住+acious形容词后缀→紧握不放的→坚韧的，顽强的",
    "tenacity": "⭐词根：ten-握住+acity名词后缀→紧握→坚韧，顽强",
    "tendency": "⭐词根：tend-延伸+ency→向某方向延伸→趋势，倾向",
    "tender": "⭐词根：tend-延伸+er→延伸出去的→柔软的，温柔的",
    "tenet": "⭐词根：ten-持有+et→所持有的东西→信条，原则",
    "tentative": "⭐词根：tent-尝试+ative→尝试性的→暂时的，试验性的",
    "tenuous": "⭐词根：ten-薄+uous→薄的→纤细的，脆弱的",
    "tepid": "⭐词根：tep-温热+id形容词后缀→微温的，不冷不热的",
    "terminal": "⭐词根：termin-界限+al→到界限的→终点的，末期的",
    "terminate": "⭐词根：termin-界限+ate→使到界限→终止，结束",
    "terminology": "⭐词根：termin-界限+ology学科→划定界限的学科→术语学，术语",
    "terrestrial": "⭐词根：terr-陆地+estial→陆地的，地球的",
    "terse": "⭐词根：ters-擦干净→语言干净利落→简洁的，精炼的",
    "testament": "⭐词根：test-证明+ament→证明的文件→遗嘱，证明",
    "testify": "⭐词根：test-证明+ify动词后缀→作证，证明",
    "testimonial": "⭐词根：test-证明+imonial→证明的东西→证明书，推荐信",
    "testimony": "⭐词根：test-证明+imony→证词，证据",
    "tether": "⭐词根：tether→栓绳→（用绳）拴住，束缚",
    "thematic": "⭐词根：them-主题+atic→主题的，题目的",
    "theology": "⭐词根：theo-神+logy学科→神学",
    "theoretical": "⭐词根：theor-观察+etical→观察思考的→理论的",
    "therapeutic": "⭐词根：therap-治疗+utic→治疗的，有疗效的",
    "thorough": "⭐词根：thorough-完全→彻底的，全面的",
    "thoroughfare": "⭐词根：thorough-完全+fare通行→完全通行→大道，通路",
    "thrifty": "⭐词根：thrift-节约+y→节约的，俭省的",
    "thrive": "⭐词根：thrive→繁荣，茁壮成长",
    "throes": "⭐词根：throe-剧痛→剧痛，阵痛",
    "throng": "⭐词根：throng-挤压→挤满，人群",
    "thwart": "⭐词根：thwart-横放→横在路上阻挡→阻挠，挫败",
    "tier": "⭐词根：tier-排列→层，等级",
    "tight": "⭐词根：tight-紧→紧的，密封的",
    "timely": "⭐词根：time时间+ly→及时的，适时的",
    "timetested": "⭐词根：time时间+tested考验→经过时间考验的",
    "timid": "⭐词根：tim-害怕+id→害怕的→胆小的，羞怯的",
    "tinge": "⭐词根：tinge-染色→微染，带有…色彩",
    "tint": "⭐词根：tint-染色→色调，色彩",
    "tip": "⭐词根：tip-尖端→尖端，小费，提示",
    "tirade": "⭐词根：tir-拉+ade→拉出一长串话→长篇抨击，长篇演说",
    "tireless": "⭐词根：tire疲劳+less无→不知疲劳的，孜孜不倦的",
    "tiresome": "⭐词根：tire疲劳+some→使人疲劳的→令人厌倦的",
    "tissue": "⭐词根：tissue-编织→编织物→组织，纸巾",
    "titanic": "⭐词根：Titan泰坦神+ic→泰坦般的→巨大的，力大无比的",
    "toady": "⭐词根：toad蟾蜍+y→像蟾蜍一样趴在地上→谄媚者，拍马屁",
    "toil": "⭐词根：toil-搅动→辛苦劳作→苦干，辛劳",
    "token": "⭐词根：token-标志→标志，象征，代币",
    "tolerable": "⭐词根：toler-容忍+able→可容忍的，尚可的",
    "tolerance": "⭐词根：toler-容忍+ance→容忍，宽容",
    "tolerant": "⭐词根：toler-容忍+ant→容忍的，宽容的",
    "tolerate": "⭐词根：toler-容忍+ate→容忍，忍受",
    "toll": "⭐词根：toll-征收→通行费，代价",
    "tome": "⭐词根：tom-切+ e →切成大块→大部头书，卷册",
    "tonic": "⭐词根：ton-音调+ic→使有音调的→滋补的，振奋的",
    "topple": "⭐词根：top顶部+ple→使顶部倒下→推翻，倒塌",
    "torment": "⭐词根：tort-扭曲+ment→扭曲的状态→折磨，痛苦",
    "tornado": "⭐词根：torn-旋转+ado→旋转的风→龙卷风",
    "torpid": "⭐词根：torp-麻木+id→麻木的→迟钝的，冬眠的",
    "torpor": "⭐词根：torp-麻木+or→麻木，迟钝，冬眠",
    "torrent": "⭐词根：torr-热+ent→热浪翻涌→激流，洪流",
    "torrid": "⭐词根：torr-热+id→热的→酷热的，热烈的",
    "tortuous": "⭐词根：tort-扭曲+uous→扭曲的→弯弯曲曲的，曲折的",
    "tout": "⭐词根：tout-到处看→招徕，兜售，吹捧",
    "towering": "⭐词根：tower塔+ing→塔一般高的→高耸的，杰出的",
    "toxic": "⭐词根：tox-毒+ic→有毒的，中毒的",
    "tractable": "⭐词根：tract-拉+able→能拉动的→易驾驭的，温顺的",
    "tradition": "⭐词根：trad-传递+ition→代代相传→传统，惯例",
    "traditional": "⭐词根：tradition传统+al→传统的，惯例的",
    "traduce": "⭐词根：tra-横穿+duc-引导+e→引到反面去→诽谤，中伤",
    "tragic": "⭐词根：trag-山羊+ic→山羊合唱的→悲剧的，悲惨的",
    "trait": "⭐词根：trait-拉→拉出的特征→特征，特点",
    "trajectory": "⭐词根：tra-横穿+ject-投掷+ory→投掷的轨迹→弹道，轨道",
    "trample": "⭐词根：tramp踩踏+le→反复踩→践踏，蹂躏",
    "tranquil": "⭐词根：tran-超越+quil-安静→非常安静→宁静的，平静的",
    "tranquility": "⭐词根：tranquil宁静+ity→宁静，平静",
    "transaction": "⭐词根：trans-交换+act行动+ion→交换行动→交易，业务",
    "transcend": "⭐词根：trans-超越+scend-爬→爬过→超越，胜过",
    "transcendent": "⭐词根：transcend超越+ent→超越的，卓越的",
    "transcribe": "⭐词根：trans-转+scrib-写+e→转写→抄写，转录",
    "transcript": "⭐词根：trans-转+script写→转写下来的东西→抄本，成绩单",
    "transfer": "⭐词根：trans-转移+fer-带来→转移过来→调动，转让",
    "transform": "⭐词根：trans-转变+form形状→转变形状→改造，变革",
    "transformation": "⭐词根：transform改造+ation→改造，转变",
    "transgress": "⭐词根：trans-超越+gress-走→走出界限→违反，越界",
    "transient": "⭐词根：trans-穿过+ient→穿过的→短暂的，转瞬即逝的",
    "transitory": "⭐词根：trans-穿过+itory→穿过的→短暂的，片刻的",
    "translucent": "⭐词根：trans-穿过+luc-光+ent→光能穿过的→半透明的",
    "transmission": "⭐词根：trans-转移+miss-发送+ion→发送转移→传送，传播",
    "transmit": "⭐词根：trans-转移+mit-发送→发送转移→传送，传播",
    "transparent": "⭐词根：trans-穿过+par-出现+ent→能看穿而出现的→透明的",
    "transplant": "⭐词根：trans-转移+plant种植→移植，移栽",
    "transport": "⭐词根：trans-转移+port-搬运→搬运转移→运输，运送",
    "traverse": "⭐词根：tra-横穿+vers-转+e→横转→横越，穿过",
    "treacherous": "⭐词根：treacher-欺骗+ous→欺骗的→背叛的，危险的",
    "treason": "⭐词根：treat-条约+son→破坏条约→叛国，背信",
    "treatise": "⭐词根：treat-处理+ise→对某问题的处理→论文，专著",
    "tremble": "⭐词根：trem-颤抖+ble→颤抖，哆嗦",
    "tremendous": "⭐词根：trem-颤抖+endous→令人颤抖的→巨大的，惊人的",
    "tremor": "⭐词根：trem-颤抖+or→颤抖，震动",
    "trench": "⭐词根：trench-切割→切割出的沟→沟渠，战壕",
    "trend": "⭐词根：trend-转向→趋势，倾向",
    "trepidation": "⭐词根：trep-害怕+id+ation→害怕的状态→惊恐，不安",
    "trial": "⭐词根：tri-三+al→三种裁决方式→审判，试验",
    "tribute": "⭐词根：tribut-给予+e→给予的东西→贡品，颂词",
    "trifle": "⭐词根：tri-三+fle→切成三份的小块→小事，琐事",
    "trigger": "⭐词根：trigger-扳机→引发，触发",
    "trim": "⭐词根：trim-整理→修剪，整理，装饰",
    "trivial": "⭐词根：tri-三+vi-路+al→三条路会合的→琐碎的，不重要的",
    "trivialize": "⭐词根：trivial琐碎的+ize→使琐碎→轻视，使显得不重要",
    "tropical": "⭐词根：trop-转+ical→太阳回归线转的地方→热带的",
    "troublesome": "⭐词根：trouble麻烦+some→麻烦的，令人烦恼的",
    "truce": "⭐词根：truce-信任→相互信任的约定→休战，停战",
    "truculent": "⭐词根：truc-凶猛+ulent→凶猛的，好斗的",
    "trudge": "⭐词根：trudge-步行→跋涉，步履艰难地走",
    "true": "⭐词根：true-真实→真实的，真正的",
    "trump": "⭐词根：trump-喇叭→王牌，胜过",
    "trumpet": "⭐词根：trump喇叭+et→小号，喇叭",
    "truncate": "⭐词根：trunc-切+ate→切断→截断，缩短",
    "trustworthy": "⭐词根：trust信任+worthy值得→值得信任的→可靠的",
    "trying": "⭐词根：try尝试+ing→考验人的→令人厌烦的，难堪的",
    "tumult": "⭐词根：tum-肿胀+ult→肿胀起来→骚动，骚乱",
    "turbid": "⭐词根：turb-搅动+id→搅浑的→浑浊的，混乱的",
    "turbulence": "⭐词根：turb-搅动+ulence→搅动的状态→骚乱，湍流",
    "turbulent": "⭐词根：turb-搅动+ulent→搅动的→骚乱的，汹涌的",
    "turgid": "⭐词根：turg-肿胀+id→肿胀的→浮肿的，浮夸的",
    "turnoil": "⭐词根：turn翻转+moil辛苦→翻来覆去辛苦→骚动，混乱",
    "turnout": "⭐词根：turn转+out出→转出来→产量，出席人数",
    "tutor": "⭐词根：tut-保护+or→保护者→导师，辅导教师",
    "tweak": "⭐词根：tweak-拧→拧，调整",
    "twinge": "⭐词根：twinge-拧→拧痛→剧痛，刺痛",
    "tycoon": "⭐词根：tycoon来自日语taikun大君→大亨，巨头",
}


def generate_memo(name, item):
    """Generate root-based memo string."""
    if name in ROOT_MEMOS:
        return ROOT_MEMOS[name]
    # Fallback: generate a basic one
    meaning1 = item.get('meaning1', '')
    cn_part = meaning1.split(':')[0].strip() if ':' in meaning1 else meaning1.split('，')[0].strip() if '，' in meaning1 else meaning1[:20]
    return f"⭐{name}→{cn_part}"


def pick_syns(item, n=4):
    """Pick up to n synonyms from available syn fields."""
    all_syns = []
    for i in range(1, 5):
        syn = item.get(f'syn{i}', '').strip()
        if syn:
            # Take first few words
            parts = [s.strip().split()[0] for s in syn.split(',') if s.strip()]
            # Remove Chinese characters
            clean_parts = [p for p in parts if not re.search(r'[\u4e00-\u9fff]', p)]
            all_syns.extend(clean_parts)
    # Deduplicate preserving order
    seen = set()
    unique = []
    for s in all_syns:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique[:n]


def pick_ants(item, n=4):
    """Pick up to n antonyms from available ant fields."""
    all_ants = []
    for i in range(1, 5):
        ant = item.get(f'ant{i}', '').strip()
        if ant:
            parts = [s.strip().split()[0] for s in ant.split(',') if s.strip()]
            clean_parts = [p for p in parts if not re.search(r'[\u4e00-\u9fff]', p)]
            all_ants.extend(clean_parts)
    seen = set()
    unique = []
    for s in all_ants:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique[:n]


def generate_example(name, item):
    """Generate a 15-20 word example sentence with <b>bold</b> word+core context."""
    eg1 = item.get('eg1', '').strip()
    eg2 = item.get('eg2', '').strip()
    eg3 = item.get('eg3', '').strip()
    
    # Pre-built examples for each word
    EXAMPLES = {
        "taxing": "The <b>taxing journey through the</b> desert exhausted the entire expedition team.",
        "tedious": "The <b>tedious lecture on tax</b> regulations lasted over three hours without a single break.",
        "teeter": "The elderly man <b>teetered on the edge of</b> the crumbling cliff before stepping back to safety.",
        "temerity": "He had the <b>temerity to challenge the</b> professor's decades-old theory during the academic conference.",
        "temper": "The manager tried to <b>temper her anger with</b> deep breaths before responding to the rude email.",
        "temperament": "The artist's volatile <b>temperament made collaboration</b> difficult but fueled her creative genius.",
        "temperate": "The scientist maintained a <b>temperate approach to</b> the controversial findings, neither praising nor condemning them.",
        "tempestuous": "Their <b>tempestuous relationship was marked by</b> passionate arguments and equally passionate reconciliations.",
        "temporal": "The philosopher pondered <b>temporal matters of the</b> physical world while dismissing spiritual concerns as irrelevant.",
        "temporary": "The construction crew erected <b>temporary shelters to house</b> workers during the six-month bridge project.",
        "tempt": "The aroma of freshly baked bread <b>tempted her to break</b> her strict diet for just one bite.",
        "tenacious": "The <b>tenacious reporter refused to</b> drop the corruption investigation despite threats from powerful officials.",
        "tenacity": "Her <b>tenacity in pursuing the</b> truth earned her the respect of colleagues throughout the journalism industry.",
        "tendency": "The stock market shows a <b>tendency to rebound after</b> sharp declines, creating opportunities for savvy investors.",
        "tender": "The nurse's <b>tender care for the</b> wounded soldiers brought comfort to the otherwise grim field hospital.",
        "tenet": "Freedom of speech is a <b>tenet upon which the</b> entire framework of democratic society is built.",
        "tentative": "The two nations reached a <b>tentative agreement to cease</b> hostilities while further negotiations took place.",
        "tenuous": "The connection between the <b>tenuous evidence and the</b> defendant's guilt was too weak to convince the jury.",
        "tepid": "The audience's <b>tepid response to the</b> performance made it clear that the play had failed to impress.",
        "terminal": "The patient was diagnosed with <b>terminal cancer and given</b> only six months to live by the doctors.",
        "terminate": "The company decided to <b>terminate the contract after</b> the vendor failed to meet multiple critical deadlines.",
        "terminology": "Learning the complex <b>terminology of molecular biology</b> was the first challenge for new graduate students.",
        "terrestrial": "The <b>terrestrial ecosystem of the</b> Amazon rainforest contains more biodiversity than any other land environment.",
        "terse": "The general's <b>terse reply to the</b> reporter's question revealed nothing but his growing irritation with the press.",
        "testament": "The ancient ruins stand as <b>testament to the once-great</b> civilization that flourished in this valley centuries ago.",
        "testify": "The witness was called to <b>testify about what she</b> had seen on the night of the robbery.",
        "testimonial": "The retiring professor received a glowing <b>testimonial from colleagues around</b> the world praising his decades of service.",
        "testimony": "The victim's emotional <b>testimony in court moved</b> the jury to deliver a guilty verdict within hours.",
        "tether": "The astronaut's safety <b>tether to the spacecraft</b> prevented him from floating away during the spacewalk.",
        "thematic": "The <b>thematic unity of the</b> novel's chapters gave the sprawling narrative a surprising sense of coherence.",
    }
    
    if name in EXAMPLES:
        return EXAMPLES[name]
    
    # Fallback: generate from eg data
    for eg in [eg1, eg2, eg3]:
        if eg:
            # Extract English part before Chinese
            eng_match = re.match(r'^([^。]*?)(\s*[。，]?\s*[\u4e00-\u9fff])', eg)
            if eng_match:
                eng_text = eng_match.group(1).strip()
            else:
                eng_text = eg.split('  ')[0].strip() if '  ' in eg else eg.strip()
            
            if eng_text and len(eng_text) > 8:
                # Bold the word + some context
                btext = eng_text.replace(name, f'<b>{name}', 1)
                # Find end of bold - include a few words after
                words = btext.split()
                for idx, w in enumerate(words):
                    if name in w:
                        bold_end = min(idx + 4, len(words))
                        words[idx] = words[idx].replace(f'<b>{name}', f'<b>{name}')
                        # Close bold after a few words
                        if bold_end < len(words):
                            words[bold_end - 1] = words[bold_end - 1] + '</b>'
                        else:
                            words[-1] = words[-1] + '</b>'
                        break
                eng_text = ' '.join(words)
                # Ensure sentence ends properly
                if not eng_text.endswith('.'):
                    eng_text += '.'
                if len(eng_text.split()) >= 10:
                    return eng_text.capitalize()
    
    # Ultimate fallback
    meaning1 = item.get('meaning1', '')
    cn = meaning1.split(':')[0].strip() if ':' in meaning1 else 'a certain quality'
    return f"The <b>{name} nature of the</b> situation required careful consideration before any action could be taken."


def generate_changkao(name, item, meaning_cn):
    """Generate changkao with specific collocations + syn/ant + GRE reading scenario."""
    
    CHANGKAO = {
        "taxing": "· 常考：taxing 形容任务/工作/旅程繁重，与 demanding、arduous 同义，与 easy、effortless 反义",
        "tedious": "· 常考：tedious 形容演讲/工作/过程冗长乏味，GRE阅读中常与 monotonous、dreary 同义替换",
        "teeter": "· 常考：teeter on the brink/edge of 摇摆于…边缘，GRE写作中描述不稳定状态，与 waver、vacillate 同义",
        "temerity": "· 常考：have the temerity to do 竟敢…，GRE阅读中贬义描述鲁莽行为，与 audacity、recklessness 同义",
        "temper": "· 常考：temper with 用…缓和，GRE阅读常考 temper 作'缓和'的动词用法，与 moderate、mitigate 同义",
        "temperament": "· 常考：by temperament 天生性情上，GRE阅读中描述艺术家/科学家的性格特质",
        "temperate": "· 常考：temperate climate/response 温和的气候/回应，GRE阅读中与 moderate、restrained 同义，与 extreme 反义",
        "tempestuous": "· 常考：tempestuous relationship/weather 激烈的关系/暴风雨天气，GRE阅读中描述激烈动荡的状态",
        "temporal": "· 常考：temporal world/affairs 世俗世界/事务，GRE阅读哲学类话题中与 spiritual、eternal 对立",
        "temporary": "· 常考：temporary solution/measure 临时方案/措施，GRE写作中与 permanent 构成对比论证",
        "tempt": "· 常考：be tempted to do 忍不住想…，tempt sb into doing 引诱某人做…，GRE阅读中常与 lure、entice 同义",
        "tenacious": "· 常考：tenacious grip/hold 紧握不松，tenacious memory 强记忆力，GRE阅读中褒义描述坚韧品质",
        "tenacity": "· 常考：with tenacity 顽强地，GRE阅读中描述成功人士的坚持品质，与 perseverance、persistence 同义",
        "tendency": "· 常考：have a tendency to do 有…的倾向，GRE阅读中描述趋势或行为模式",
        "tender": "· 常考：tender care/concern 温柔的关怀，tender offer 招标，GRE阅读中作'柔嫩/温柔'解",
        "tenet": "· 常考：central/fundamental tenet 核心/基本信条，GRE阅读哲学/政治类文章中描述核心理念",
        "tentative": "· 常考：tentative agreement/conclusion 临时协议/初步结论，GRE阅读中与 preliminary、provisional 同义",
        "tenuous": "· 常考：tenuous connection/link 脆弱的联系/微弱的关联，GRE阅读逻辑题中描述weak argument",
        "tepid": "· 常考：tepid reception/response 冷淡的接待/反应，GRE阅读中描述缺乏热情的态度",
        "terminal": "· 常考：terminal disease/patient 晚期疾病/病人，terminal degree 最高学位，GRE阅读中与 final、fatal 相关",
        "terminate": "· 常考：terminate a contract/relationship 终止合同/关系，GRE阅读中与 end、cease 同义替换",
        "terminology": "· 常考：technical/scientific terminology 技术/科学术语，GRE阅读中学科类文章高频词",
        "terrestrial": "· 常考：terrestrial planet/ecosystem 类地行星/陆地生态系统，GRE阅读天文/生态类话题中与 aquatic、celestial 对立",
        "terse": "· 常考：terse reply/statement 简洁的回答/声明，GRE阅读中正面描述语言简洁有力",
        "testament": "· 常考：a testament to 是…的证明，GRE阅读中作'证明'解，与 testimony、evidence 相关",
        "testify": "· 常考：testify to sth 证明…，testify against 作证不利于，GRE阅读法律类文章高频词",
        "testimonial": "· 常考：glowing testimonial 热情的推荐信，GRE阅读中描述对某人能力/品德的证明",
        "testimony": "· 常考：bear testimony to 为…作证，GRE阅读法律/历史类文章中与 evidence 同义",
        "tether": "· 常考：at the end of one's tether 山穷水尽/忍无可忍，GRE阅读中比喻用法表示受限制",
        "thematic": "· 常考：thematic unity/concern 主题统一/关注，GRE阅读文学/艺术评论中描述文本结构",
    }
    
    if name in CHANGKAO:
        return CHANGKAO[name]
    
    # Fallback: generate dynamically
    syns = pick_syns(item, 3)
    ants = pick_ants(item, 3)
    syn_str = '、'.join(syns) if syns else '相关同义词'
    ant_str = '、'.join(ants) if ants else '相关反义词'
    
    pos = item.get('pos1', '').strip('. ')
    cn_part = meaning_cn.split('.')[-1] if '.' in meaning_cn else meaning_cn
    return f"· 常考：{name} 作为{pos}表示「{cn_part}」，GRE阅读中与 {syn_str} 同义，与 {ant_str} 反义"


def generate_exam_tips(item):
    """Generate exam_tips: 💡同义3-4 | 反义3-4"""
    syns = pick_syns(item, 4)
    ants = pick_ants(item, 4)
    
    # Ensure we have at least some
    syn_str = ', '.join(syns) if syns else 'similar meaning synonyms'
    ant_str = ', '.join(ants) if ants else 'related antonyms'
    
    return f"💡同义：{syn_str} | 反义：{ant_str}"


# ── Main processing ──
results = []

for item in data:
    name = item['name']
    
    # --- meaning_cn ---
    pos1 = item.get('pos1', '')
    meaning1 = item.get('meaning1', '')
    pos2 = item.get('pos2', '')
    meaning2 = item.get('meaning2', '')
    
    cn_parts = []
    if meaning1 and ':' in meaning1:
        cn_part = meaning1.split(':')[0].strip()
        cn_parts.append(cn_part)
    elif meaning1:
        cn_part = meaning1.split('，')[0].strip() if '，' in meaning1 else meaning1.strip()
        cn_parts.append(cn_part)
    
    if meaning2 and pos2:
        if ':' in meaning2:
            cn2 = meaning2.split(':')[0].strip()
        else:
            cn2 = meaning2.split('，')[0].strip() if '，' in meaning2 else meaning2.strip()
        if cn2 and cn2 not in cn_parts:
            cn_parts.append(cn2)
    
    cn_parts = cn_parts[:2]
    
    def clean_p(s):
        s = re.sub(r'[（(][^）)]*[）)]', '', s)
        s = re.sub(r'[\[][^\[\]]*[\]]', '', s)
        return s.strip('，,;: ')
    
    pos_prefix = pos1.strip('. ') if pos1 else ''
    if cn_parts:
        first = clean_p(cn_parts[0]).strip('，, ')
        if len(cn_parts) > 1:
            second = clean_p(cn_parts[1]).strip('，, ')
            if first and second and second not in first:
                meaning_cn = f"{pos_prefix}.{first}，{second}"
            else:
                meaning_cn = f"{pos_prefix}.{first}" if first else f"{pos_prefix}."
        else:
            meaning_cn = f"{pos_prefix}.{first}" if first else f"{pos_prefix}."
    else:
        meaning_cn = f"{pos_prefix}."
    
    meaning_cn = meaning_cn.replace('，，', '，').strip('，; ')
    
    memo = generate_memo(name, item)
    example = generate_example(name, item)
    changkao = generate_changkao(name, item, meaning_cn)
    exam_tips = generate_exam_tips(item)
    
    result = {
        "name": name,
        "meaning_cn": meaning_cn,
        "memo": memo,
        "example": example,
        "changkao": changkao,
        "exam_tips": exam_tips
    }
    results.append(result)

# Write output
with open('/home/Lu/gre_batch_9_done.json', 'w') as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

print(f"Done. {len(results)} words written to /home/Lu/gre_batch_9_done.json")

# Verify a few
for r in results[:3]:
    print(json.dumps(r, ensure_ascii=False))
print("...")
for r in results[-3:]:
    print(json.dumps(r, ensure_ascii=False))
