#!/usr/bin/env python3
"""
Process 306 GRE words (fetid → indifferent) into formatted JSON lines.
Each line: {"name", "meaning_cn", "memo", "example", "changkao", "exam_tips"}
"""
import json, re

with open('/home/Lu/gre_batch_4_raw.json', 'r') as f:
    data = json.load(f)

# ===== ROOT/ETYMOLOGY DATABASE for 306 words =====
# Hand-crafted 词根拆解 for every word in this batch
ROOTS = {
    "fetid": "⭐词根：fet-恶臭+id→恶臭的",
    "fetter": "⭐词根：fet-脚+er→脚镣→束缚",
    "fiasco": "⭐词根：源自意大利语\"做瓶子\"，做坏了的瓶子→大失败",
    "fickle": "⭐词根：与fight同源，见异思迁→易变的",
    "fictitious": "⭐词根：fict-虚构+itious→虚构的",
    "fidelity": "⭐词根：fid-信任+elity→忠实",
    "figurative": "⭐词根：figur-形状+ative→比喻的",
    "figurine": "⭐词根：figur-形状+ine小→小雕像",
    "filibuster": "⭐词根：fil-线+buster破坏者→用冗长演说破坏议程",
    "filter": "⭐词根：filtr-过滤+er→过滤器",
    "finale": "⭐词根：fin-结束+ale→终曲",
    "finesse": "⭐词根：fin-结束+esse→精细处理→技巧",
    "finicky": "⭐词根：fin-精细+icky→过分讲究的",
    "flaccid": "⭐词根：flacc-松弛+id→松弛的",
    "flag": "⭐词根：flag-下垂→衰退",
    "flamboyant": "⭐词根：flam-火焰+boyant→火焰般闪耀→浮夸的",
    "flatter": "⭐词根：flatt-平坦+er→使平坦→奉承",
    "flaw": "⭐词根：flaw-裂缝→缺陷",
    "fledgling": "⭐词根：fledg-羽毛+ling小→刚长羽毛的小鸟→新手",
    "fleet": "⭐词根：fleet-流动→快速的；车队",
    "flexible": "⭐词根：flex-弯曲+ible→易弯曲的→灵活的",
    "flinch": "⭐词根：flinch-退缩→畏缩",
    "flippancy": "⭐词根：flip-轻弹+ancy→轻率",
    "flirt": "⭐词根：flirt-甩动→调情",
    "flit": "⭐词根：flit-掠过→轻快地飞过",
    "flock": "⭐词根：flock-聚集→羊群；成群",
    "florid": "⭐词根：flor-花+id→像花一样的→华丽的",
    "flounder": "⭐词根：flounder-挣扎→错乱地行事",
    "flourish": "⭐词根：flour-花+ish→开花→繁荣",
    "flout": "⭐词根：flout-吹笛子(拟声)→嘲笑",
    "fluctuate": "⭐词根：fluct-流动+uate→波动",
    "fluent": "⭐词根：flu-流动+ent→流利的",
    "fluky": "⭐词根：fluke-侥幸+ y→侥幸的",
    "flush": "⭐词根：flush-急流→脸红；充裕的",
    "fluster": "⭐词根：fluster-慌乱→使慌张",
    "foible": "⭐词根：foible-薄弱→小缺点",
    "foil": "⭐词根：foil-叶片→箔；挫败",
    "foment": "⭐词根：fom-暖敷+ent→引发，煽动",
    "foolproof": "⭐词根：fool傻瓜+proof防→傻瓜都会用的→简单安全的",
    "footloose": "⭐词根：foot脚+loose松→脚松了→自由自在的",
    "forbearance": "⭐词根：for-完全+bear忍受+ance→忍耐",
    "forebear": "⭐词根：fore-前+bear生→祖先",
    "forestall": "⭐词根：fore-前+stall放→预先阻止",
    "foreword": "⭐词根：fore-前+word话→前言",
    "forge": "⭐词根：forge锻造→伪造；锻造",
    "formidable": "⭐词根：formid-恐惧+able→可怕的",
    "forthright": "⭐词根：forth向前+right直→直率的",
    "fortify": "⭐词根：fort-强+ify→加固",
    "foster": "⭐词根：foster-(与food同源)→养育",
    "founder": "⭐词根：found底+er→沉没；失败",
    "fracas": "⭐词根：frac-破碎+as→喧嚷，吵闹",
    "fracture": "⭐词根：fract-破+ure→骨折；断裂",
    "fragile": "⭐词根：frag-破碎+ile易→易碎的",
    "frail": "⭐词根：frail(=frag)破碎→脆弱的",
    "fraudulent": "⭐词根：fraud-欺骗+ulent→欺骗性的",
    "fraught": "⭐词根：fraught-装满→充满的",
    "frenzy": "⭐词根：fren-狂乱+zy→疯狂",
    "frequent": "⭐词根：frequ-频繁+ent→频繁的",
    "fretful": "⭐词根：fret-烦恼+ful→烦躁的",
    "friable": "⭐词根：fri-碎+able→易碎的",
    "friction": "⭐词根：frict-摩擦+ion→摩擦",
    "frigid": "⭐词根：frig-冷+id→寒冷的",
    "fringe": "⭐词根：fringe-边缘→边缘；刘海",
    "frivolous": "⭐词根：frivol-愚蠢+ous→轻浮的",
    "frothy": "⭐词根：froth泡沫+y→起泡的；空洞的",
    "frowsy": "⭐词根：frowsy-发霉的→邋遢的",
    "frugal": "⭐词根：frug-节约+al→节俭的",
    "frustrate": "⭐词根：frustr-徒劳+ate→挫败",
    "full-bodied": "⭐词根：full充满+bodied身体→醇厚的",
    "fulminate": "⭐词根：fulmin-闪电+ate→猛烈谴责",
    "fumble": "⭐词根：fumble-摸索→笨拙地处理",
    "furor": "⭐词根：fur-愤怒+or→狂怒",
    "furtive": "⭐词根：furt-偷+ive→偷偷摸摸的",
    "fury": "⭐词根：fur-愤怒+y→暴怒",
    "fussy": "⭐词根：fuss-大惊小怪+y→爱挑剔的",
    "futile": "⭐词根：fut-倒出+ile→易倒空的→无用的",
    "gadfly": "⭐词根：gad尖棒+fly苍蝇→牛虻→讨人厌的人",
    "gaffe": "⭐词根：gaffe-(法语)铁钩→失礼，出丑",
    "gainsay": "⭐词根：gain-反对+say说→否认",
    "gall": "⭐词根：gall-胆汁→怨恨；厚颜",
    "gallant": "⭐词根：gall-炫耀+ant→英勇的",
    "galvanize": "⭐词根：galvan-电流+ize→电击→激起",
    "gamble": "⭐词根：gamble-赌博→冒险",
    "gambol": "⭐词根：gamb-腿+ol→跳跃，嬉戏",
    "gangly": "⭐词根：gang-走+ly→走路摇晃→瘦长难看的",
    "garble": "⭐词根：garble-筛选→断章取义",
    "gargantuan": "⭐词根：Gargantua《巨人传》中人物→巨大的",
    "garish": "⭐词根：gar-装饰+ish→过分装饰的→花哨的",
    "garment": "⭐词根：gar-装饰+ment→衣服",
    "garrulous": "⭐词根：garr-唠叨+ulous→喋喋不休的",
    "gash": "⭐词根：gash-深砍→深伤口",
    "gasification": "⭐词根：gas气体+ification→气化",
    "gauche": "⭐词根：gauche-(法语)左→笨拙的，不圆滑的",
    "gaudy": "⭐词根：gaud-华丽+y→俗丽的",
    "gauge": "⭐词根：gauge-测量→标准量规；测量",
    "gear": "⭐词根：gear-齿轮→装备",
    "genial": "⭐词根：gen-出生+ial→天生的和蔼→亲切的",
    "genteel": "⭐词根：gent-绅士+eel→有教养的",
    "germane": "⭐词根：germ-芽+ane→同源的→相关的",
    "gibe": "⭐词根：gibe-嘲弄→嘲笑",
    "giddy": "⭐词根：giddy-神(与god同源)→头晕的",
    "gild": "⭐词根：gild-镀金→装饰",
    "gist": "⭐词根：gist-要点→主旨",
    "gladiator": "⭐词根：glad-剑+iator→角斗士",
    "glaze": "⭐词根：glaze-玻璃→上釉；变呆滞",
    "glib": "⭐词根：glib-光滑的→口齿伶俐的",
    "glisten": "⭐词根：glist-闪烁+en→闪光",
    "glitch": "⭐词根：glitch-小故障→小毛病",
    "gloat": "⭐词根：gloat-盯视→幸灾乐祸",
    "gloomy": "⭐词根：gloom-阴暗+y→忧郁的",
    "gloss": "⭐词根：gloss-舌头→注释；光泽",
    "glossy": "⭐词根：gloss-光泽+y→有光泽的",
    "glut": "⭐词根：glut-吞没→过量供应",
    "glutinous": "⭐词根：glutin-胶+ous→粘的",
    "glutton": "⭐词根：glut-吞+ton→贪吃者",
    "goad": "⭐词根：goad-尖刺→刺激",
    "gobble": "⭐词根：gobble-拟声→狼吞虎咽",
    "goggle": "⭐词根：goggle-瞪眼→护目镜",
    "goldbrick": "⭐词根：gold金+brick砖→假金砖→逃避工作的人",
    "gorge": "⭐词根：gorge-咽喉→峡谷；狼吞虎咽",
    "gossamer": "⭐词根：gos鹅+sam-夏天→鹅在夏天的绒毛→薄纱",
    "gourmand": "⭐词根：gourmand-贪吃→美食家(贬)",
    "gourmet": "⭐词根：gourmet-(法语)美食家(褒)",
    "grandeur": "⭐词根：grand-大+eur→宏伟",
    "grandiloquent": "⭐词根：grand大+loqu说+ent→说大话的",
    "grandiose": "⭐词根：grand-大+iose→宏大的；浮夸的",
    "grandstand": "⭐词根：grand大+stand站→坐大看台→哗众取宠",
    "grate": "⭐词根：grate-擦→磨碎；使人烦躁",
    "gratify": "⭐词根：grat-使高兴+ify→使满足",
    "gratuitous": "⭐词根：gratuit-免费+ous→免费的；无理由的",
    "green": "⭐词根：green-绿色→缺乏经验的",
    "gregarious": "⭐词根：greg-群+arious→群居的→爱社交的",
    "grieve": "⭐词根：griev-沉重+e→悲伤",
    "grimace": "⭐词根：grim-可怕+ace→鬼脸",
    "grin": "⭐词根：grin-咧嘴→露齿笑",
    "gripe": "⭐词根：gripe-抓→抱怨；肠绞痛",
    "grisly": "⭐词根：gris-恐怖+ly→可怕的",
    "groove": "⭐词根：groove-沟槽→常规；最佳状态",
    "grotesque": "⭐词根：grot-洞穴+esque→洞穴画→奇形怪状的",
    "grovel": "⭐词根：grovel-趴→匍匐；卑躬屈膝",
    "grueling": "⭐词根：gruel-稀粥+ing→喝稀粥般的→折磨人的",
    "guile": "⭐词根：guile-诡计→狡猾",
    "guilt": "⭐词根：guilt-罪过→内疚",
    "gull": "⭐词根：gull-欺骗→欺骗；海鸥",
    "gullible": "⭐词根：gull-欺骗+ible→易受骗的",
    "gush": "⭐词根：gush-涌出→滔滔不绝地说",
    "gust": "⭐词根：gust-风味→一阵狂风；品味",
    "guzzle": "⭐词根：guzzle-拟声(咕噜咕噜)→狂饮",
    "hack": "⭐词根：hack-砍→乱砍；雇佣文人",
    "hackneyed": "⭐词根：Hackney伦敦一地名(出租马)->陈腐的",
    "halcyon": "⭐词根：halcyon-翠鸟→冬至时翠鸟筑巢→平静的",
    "hale": "⭐词根：hale-健康(whole同源)→强壮的",
    "half-baked": "⭐词根：half半+baked烤→半生不熟的→不成熟的",
    "hallmark": "⭐词根：hall大厅+mark标记→伦敦金匠厅印记→标志",
    "hallow": "⭐词根：hallow-神圣(holy同源)→视为神圣",
    "hallucination": "⭐词根：hallucin-幻想+ation→幻觉",
    "ham-handed": "⭐词根：ham火腿+handed手→像火腿一样的手→笨手笨脚的",
    "hammer": "⭐词根：hammer-锤子→敲打",
    "hamper": "⭐词根：hamper-束缚→妨碍",
    "hamstring": "⭐词根：ham腿+string筋→割断腿筋→使瘫痪",
    "hangdog": "⭐词根：hang挂+dog狗→像狗一样垂头→羞愧的",
    "hanker": "⭐词根：hanker-渴望→向往",
    "haphazard": "⭐词根：hap运气+hazard冒险→偶然的",
    "harangue": "⭐词根：har-召集+angue→长篇演说",
    "harass": "⭐词根：harass-反复攻击→骚扰",
    "harbinger": "⭐词根：harb-住宿+inger→先遣投宿者→先驱",
    "harbor": "⭐词根：harb-住+or→港口；庇护",
    "hard-bitten": "⭐词根：hard硬+bitten咬→咬得硬的→坚韧的",
    "hardy": "⭐词根：hard-硬+y→强壮的；耐寒的",
    "harmonious": "⭐词根：harmon-和谐+ious→和谐的",
    "harness": "⭐词根：harness-马具→利用；治理",
    "harrow": "⭐词根：harrow-耙→折磨",
    "harry": "⭐词根：harry-掠夺→不断骚扰",
    "harsh": "⭐词根：harsh-粗糙→严厉的",
    "hasten": "⭐词根：hast-快+en→催促",
    "hasty": "⭐词根：hast-快+y→仓促的",
    "haunt": "⭐词根：haunt-常去→萦绕；常出没",
    "hauteur": "⭐词根：haut-高+eur→高傲",
    "haven": "⭐词根：hav-持有+en→安全港",
    "havoc": "⭐词根：havoc-掠夺→大破坏",
    "headlong": "⭐词根：head头+long长→头向前→轻率的",
    "hearken": "⭐词根：hear听+ken→倾听",
    "hearten": "⭐词根：heart心+en→鼓励",
    "heartrending": "⭐词根：heart心+rend撕裂+ing→心碎的",
    "hedonism": "⭐词根：hedon-快乐+ism→享乐主义",
    "hegemony": "⭐词根：hegemon-领导+y→霸权",
    "heinous": "⭐词根：hein-恨+ous→可憎的",
    "hew": "⭐词根：hew-砍→砍伐",
    "herald": "⭐词根：her-军队+ald→传令官→先驱",
    "heresy": "⭐词根：heres-选择+y→异端邪说",
    "heretical": "⭐词根：heretic-异教徒+al→异端的",
    "hermetic": "⭐词根：Hermes赫尔墨斯+tic→密封的(赫尔墨斯发明密封术)",
    "hesitance": "⭐词根：hesit-犹豫+ance→犹豫",
    "heterodox": "⭐词根：hetero-异+dox观点→异端的",
    "hidebound": "⭐词根：hide皮+bound绑→裹着皮的→保守的",
    "hideous": "⭐词根：hide-隐藏+ous→丑得藏起来的→丑陋的",
    "hie": "⭐词根：hie-快走→疾行",
    "hike": "⭐词根：hike-远足→徒步旅行",
    "hilarious": "⭐词根：hilar-高兴+ious→欢闹的",
    "histrionic": "⭐词根：histrion-演员+ic→戏剧的；做作的",
    "hive": "⭐词根：hive-蜂房→蜂群；忙碌场所",
    "hoard": "⭐词根：hoard-宝藏→囤积",
    "hoary": "⭐词根：hoar-灰白+y→灰白的；古老的",
    "hoax": "⭐词根：hoax-欺骗→恶作剧",
    "hodgepodge": "⭐词根：hodge+podge→大杂烩",
    "homage": "⭐词根：hom-人+age→臣服于领主的仪式→敬意",
    "homely": "⭐词根：home家+ly→家常的→朴素的",
    "homily": "⭐词根：hom-人+ily→布道",
    "homogenize": "⭐词根：homo-相同+gen产生+ize→使均匀",
    "hone": "⭐词根：hone-磨刀石→磨练",
    "hoodwink": "⭐词根：hood头巾+wink眨眼→蒙眼→欺骗",
    "hortative": "⭐词根：hort-鼓励+ative→劝告的",
    "hovel": "⭐词根：hovel-棚屋→简陋小屋",
    "hubris": "⭐词根：hubris-(希腊)傲慢→自大",
    "humble": "⭐词根：hum-地面+ble→谦卑的",
    "humility": "⭐词根：hum-地面+ility→谦逊",
    "humor": "⭐词根：humor-体液(古生理学)→幽默",
    "hurricane": "⭐词根：hurricane-飓风(源自玛雅神Huracan)→风暴",
    "husband": "⭐词根：hus-家+band束缚→持家者→节俭使用",
    "husk": "⭐词根：husk-外壳→外皮",
    "husky": "⭐词根：husk外壳+y→声音沙哑的；哈士奇",
    "hybrid": "⭐词根：hybrid-杂交→混合物",
    "hymn": "⭐词根：hymn-赞美诗→圣歌",
    "hyperbole": "⭐词根：hyper-超过+bole扔→夸张法",
    "hypnotic": "⭐词根：hypn-睡眠+otic→催眠的",
    "hypocritical": "⭐词根：hypo-下+crit-判断+ical→伪善的",
    "iconoclast": "⭐词根：icon-偶像+clast破坏→打破偶像者",
    "idolatrize": "⭐词根：idol-偶像+atrize→盲目崇拜",
    "idyll": "⭐词根：idyll-田园诗→愉快时光",
    "ignite": "⭐词根：ign-火+ite→点燃",
    "ignominy": "⭐词根：ig-不+nomin-名字+y→无名→耻辱",
    "illiteracy": "⭐词根：il-不+liter-文字+acy→文盲",
    "illuminati": "⭐词根：il-里面+lumin-光+ati→光明会→先觉者",
    "illuminate": "⭐词根：il-里面+lumin-光+ate→照亮",
    "illusory": "⭐词根：il-进来+lus-玩耍+ory→幻觉的",
    "imbibe": "⭐词根：im-进入+bibe-喝→喝；吸收",
    "imbroglio": "⭐词根：im-进入+broglio混乱→错综复杂局面",
    "imitation": "⭐词根：imit-模仿+ation→模仿",
    "immaculate": "⭐词根：im-无+macul-斑点+ate→无斑点的→纯洁的",
    "immanent": "⭐词根：im-在内+man-停留+ent→内在的",
    "immaterial": "⭐词根：im-无+material物质→非物质的",
    "immature": "⭐词根：im-不+mature成熟→不成熟的",
    "immemorial": "⭐词根：im-不+memor-记忆+ial→记忆之外的→远古的",
    "immune": "⭐词根：im-无+mumm-服务+e→免除的→免疫的",
    "immure": "⭐词根：im-进入+mur-墙+e→监禁",
    "immutable": "⭐词根：im-不+mut-改变+able→不可变的",
    "impassive": "⭐词根：im-不+pass-感情+ive→无感情的→冷漠的",
    "impeccable": "⭐词根：im-无+pecc-罪行+able→无罪的→完美的",
    "impecunious": "⭐词根：im-无+pecuni-钱+ous→没钱的→贫穷的",
    "impede": "⭐词根：im-进入+ped-脚+e→把脚放进去→妨碍",
    "impending": "⭐词根：im-向下+pend-悬挂+ing→悬在头上→逼近的",
    "impenetrable": "⭐词根：im-不+penetr-穿透+able→不可穿透的",
    "impenitent": "⭐词根：im-不+penitent懊悔→不悔悟的",
    "imperative": "⭐词根：im-使+per-准备+ative→紧急的",
    "imperial": "⭐词根：imper-统治+ial→帝国的",
    "imperious": "⭐词根：imper-统治+ious→专横的",
    "impertinent": "⭐词根：im-不+pertinent→不恰当的→无礼的",
    "imperturbable": "⭐词根：im-不+perturb-扰乱+able→冷静的",
    "impervious": "⭐词根：im-不+per-通过+vious→不可渗透的",
    "impetuous": "⭐词根：im-向+pet-冲+uous→冲动的",
    "impious": "⭐词根：im-不+pious虔诚→不敬的",
    "implacable": "⭐词根：im-不+plac-平静+able→无法平息的",
    "implement": "⭐词根：im-内+ple-装满+ment→工具；实施",
    "implode": "⭐词根：im-向内+plode-爆炸→内爆",
    "imposing": "⭐词根：im-在上+pos-放+ing→放在上面的→壮观的",
    "importune": "⭐词根：im-进入+port-港口+une→进港纠缠→强求",
    "impostor": "⭐词根：im-进入+post-放+or→冒充者",
    "impotent": "⭐词根：im-无+pot-力量+ent→无力的",
    "imprecise": "⭐词根：im-不+precise精确→不精确的",
    "impromptu": "⭐词根：im-不+promptu-准备→即席的",
    "improvise": "⭐词根：im-不+pro-前+vis-看+e→临时准备→即兴创作",
    "imprudent": "⭐词根：im-不+prudent谨慎→轻率的",
    "impudent": "⭐词根：im-不+prud-谨慎+ent→厚颜无耻的",
    "impugn": "⭐词根：im-进入+pugn-打→抨击",
    "impuissance": "⭐词根：im-无+puissance力量→无力",
    "inadvertent": "⭐词根：in-不+advert-注意+ent→不注意的→疏忽的",
    "inalienable": "⭐词根：in-不+alien-外来的+able→不可剥夺的",
    "inane": "⭐词根：in-空+ane→空洞的",
    "inanimate": "⭐词根：in-无+anim-生命+ate→无生命的",
    "inaugurate": "⭐词根：in-进入+augur-占卜+ate→举行就职典礼",
    "incandescent": "⭐词根：in-进入+cand-白热+escent→白炽的",
    "incantation": "⭐词根：in-进入+cant-唱+ation→念咒",
    "incarnate": "⭐词根：in-进入+carn-肉+ate→化身的",
    "incendiary": "⭐词根：incend-火+iary→纵火的",
    "incense": "⭐词根：in-进入+cense-点燃→激怒；香",
    "inception": "⭐词根：in-进入+cept-拿+ion→开端",
    "incessant": "⭐词根：in-不+cess-停止+ant→不断的",
    "inch": "⭐词根：inch-英寸→缓慢移动",
    "inchoate": "⭐词根：in-进入+choat-开始+e→初期的",
    "incinerate": "⭐词根：in-进入+cin-灰+erate→烧成灰",
    "incipient": "⭐词根：in-进入+cip-开始+ient→初期的",
    "incite": "⭐词根：in-进入+cit-唤起+e→煽动",
    "inclement": "⭐词根：in-不+clement仁慈→严酷的(天气)",
    "incogitant": "⭐词根：in-不+cogit-思考+ant→不思考的→轻率的",
    "incongruent": "⭐词根：in-不+congru-一致+ent→不一致的",
    "inconsequential": "⭐词根：in-不+consequent-结果+ial→不重要的",
    "incontrovertible": "⭐词根：in-不+contro-反对+vert-转+ible→无可辩驳的",
    "incorrigible": "⭐词根：in-不+corrig-改正+ible→不可救药的",
    "incriminate": "⭐词根：in-进入+crimin-罪+ate→指控",
    "incubate": "⭐词根：in-上+cub-躺+ate→孵化",
    "inculpate": "⭐词根：in-进入+culp-罪+ate→归罪",
    "incursion": "⭐词根：in-进入+cur-跑+sion→入侵",
    "indelible": "⭐词根：in-不+del-擦除+ible→不可擦除的",
    "indemnity": "⭐词根：in-不+demn-伤害+ity→赔偿",
    "indict": "⭐词根：in-进入+dict-说→指控",
    "indifferent": "⭐词根：in-不+different不同→中立的→冷漠的",
}

# ===== ANTONYM ENHANCEMENTS =====
# For words without ant1 or with incomplete antonyms, provide common GRE antonyms
EXTRA_ANTS = {
    "fetter(n)": "freedom, liberation, emancipation 自由",
    "fetter(v)": "enfranchise, free, liberate, unbind, facilitate",
    "fiasco": "blockbuster, eclat, success 成功",
    "fidelity": "disloyalty, treachery 不忠",
    "fickle": "loyal, constant, steadfast 忠诚的",
    "fictitious": "genuine, authentic, real 真实的",
    "flamboyant": "subdued, restrained, modest 低调的",
    "flaccid": "firm, taut, rigid 坚硬的",
    "flexible": "rigid, inflexible, stiff 僵硬的",
    "flinch": "soldier, stand firm 不畏缩",
    "flippancy": "seriousness, solemnity, respect 严肃",
    "florid": "plain, simple, austere 朴素的",
    "flourish": "wither, decline, decay 衰落",
    "flout": "respect, obey, honor 尊重",
    "fluctuate": "stabilize, remain constant 稳定",
    "fluent": "halting, hesitant, stammering 结巴的",
    "foible": "merit, strength, forte 优点",
    "foment": "quell, suppress, allay 平息",
    "forbearance": "impatience, intolerance 急躁",
    "forestall": "facilitate, promote, expedite 促进",
    "formidable": "weak, feeble, trivial 微不足道的",
    "fortify": "weaken, undermine, enervate 削弱",
    "foster": "stifle, suppress, discourage 抑制",
    "fragile": "strong, tough, sturdy 强壮的",
    "frail": "robust, strong, sturdy 强健的",
    "fraudulent": "authentic, genuine, honest 真实的",
    "frenzy": "calm, serenity, peace 平静",
    "frequent": "infrequent, rare, seldom 罕见的",
    "fretful": "placid, serene, calm 平静的",
    "friction": "harmony, accord, agreement 和谐",
    "frigid": "warm, hot, tropical 温暖的",
    "frivolous": "serious, solemn, earnest 严肃的",
    "frugal": "extravagant, wasteful, lavish 奢侈的",
    "frustrate": "facilitate, promote, assist 促进",
    "furtive": "open, candid, forthright 公开的",
    "futile": "useful, productive, effective 有效的",
    "gainsay": "confirm, affirm, admit 承认",
    "gallant": "cowardly, timid, craven 胆小的",
    "galvanize": "discourage, dampen, deter 使沮丧",
    "garrulous": "taciturn, laconic, reticent 寡言的",
    "gauche": "graceful, polished, urbane 优雅的",
    "gaudy": "elegant, refined, tasteful 雅致的",
    "genial": "unfriendly, cold, hostile 不友好的",
    "germane": "irrelevant, extraneous, unrelated 无关的",
    "glib": "halting, hesitant, earnest 迟疑的",
    "gloomy": "cheerful, bright, optimistic 乐观的",
    "glut": "shortage, scarcity, dearth 短缺",
    "gratuitous": "justified, warranted, necessary 合理的",
    "gregarious": "unsociable, aloof, reclusive 不爱社交的",
    "gullible": "astute, shrewd, discerning 精明的",
    "hackneyed": "novel, original, innovative 新颖的",
    "halcyon": "stormy, turbulent, chaotic 暴风雨的",
    "haphazard": "deliberate, systematic, planned 有计划的",
    "harass": "soothe, comfort, reassure 安抚",
    "harsh": "mild, gentle, lenient 温和的",
    "hasty": "deliberate, cautious, slow 谨慎的",
    "haughty": "humble, modest, meek 谦逊的",
    "headlong": "cautious, deliberate, wary 谨慎的",
    "heinous": "admirable, commendable, laudable 可嘉的",
    "hermetic": "open, accessible, porous 开放的",
    "heterodox": "orthodox, conventional, mainstream 正统的",
    "hidebound": "open-minded, progressive 开明的",
    "homely": "beautiful, attractive, comely 美丽的",
    "hoodwink": "disabuse, enlighten, undeceive 使醒悟",
    "hubris": "humility, modesty, meekness 谦逊",
    "hyperbole": "understatement, litotes 轻描淡写",
    "hypocritical": "sincere, genuine, honest 真诚的",
    "iconoclast": "traditionalist, conformist 传统主义者",
    "idolatrize": "despise, scorn, criticize 鄙视",
    "ignominy": "honor, glory, renown 荣誉",
    "illuminate": "darken, obscure, dim 使暗淡",
    "illusory": "real, actual, genuine 真实的",
    "immaculate": "stained, tainted, impure 不洁的",
    "immature": "mature, adult, developed 成熟的",
    "immune": "susceptible, vulnerable 易受影响的",
    "immutable": "mutable, changeable, variable 可变的",
    "impassive": "emotional, passionate, expressive 热情的",
    "impeccable": "flawed, defective, imperfect 有缺陷的",
    "impecunious": "wealthy, affluent, prosperous 富有的",
    "impede": "facilitate, expedite, hasten 促进",
    "impenetrable": "penetrable, permeable 可穿透的",
    "imperious": "submissive, humble, meek 谦卑的",
    "impertinent": "polite, respectful, courteous 礼貌的",
    "imperturbable": "excitable, agitated, nervous 易激动的",
    "impervious": "vulnerable, receptive, permeable 可渗透的",
    "impetuous": "cautious, deliberate, prudent 谨慎的",
    "implacable": "forgiving, lenient, merciful 宽容的",
    "imposing": "unimpressive, insignificant 不起眼的",
    "impotent": "powerful, strong, potent 强大的",
    "imprudent": "prudent, wise, cautious 谨慎的",
    "inadvertent": "intentional, deliberate, premeditated 故意的",
    "inane": "meaningful, profound, sensible 有意义的",
    "incessant": "intermittent, sporadic, occasional 间歇的",
    "incite": "quell, suppress, deter 镇压",
    "inclement": "mild, temperate, pleasant 温和的",
    "incongruent": "congruent, consistent, compatible 一致的",
    "incontrovertible": "disputable, questionable 有争议的",
    "incorrigible": "reformable, corrigible 可改正的",
    "indelible": "erasable, removable, temporary 可擦除的",
    "indifferent": "attentive, concerned, interested 关心的",
}

# ===== EXAMPLE ENHANCEMENTS =====
# For words that lack good examples in source data, provide curated ones
CURATED_EXAMPLES = {}


def extract_cn(meaning):
    """Extract Chinese part before colon, clean parentheses."""
    if not meaning:
        return ""
    if ":" in meaning:
        cn = meaning.split(":")[0].strip()
    else:
        cn = meaning
    # Remove parenthetical content
    cn = re.sub(r'[（(][^）)]*[）)]', '', cn)
    cn = re.sub(r'[（(][^)]*[）)]', '', cn)
    cn = cn.rstrip('，,；;、 ')
    return cn


def extract_en(meaning):
    """Extract English part after colon."""
    if not meaning:
        return ""
    if ":" in meaning:
        return meaning.split(":", 1)[1].strip()
    return meaning


def clean_syn_ant(text):
    """Extract only English words from syn/ant fields, removing Chinese chars, keeping commas."""
    if not text:
        return ""
    # Remove Chinese characters completely
    en_only = re.sub(r'[\u4e00-\u9fff；;，、。]+', '', text)
    # Normalize whitespace around commas
    en_only = re.sub(r'\s*,\s*', ', ', en_only)
    # Collapse multiple spaces
    en_only = re.sub(r'\s+', ' ', en_only).strip()
    # Remove leading/trailing punctuation
    en_only = en_only.strip(' ,|;')
    return en_only


def build_example(name, item):
    """Build a 15-20 word example sentence with <b> bold."""
    examples = []
    for key in ['eg1', 'eg2', 'eg3']:
        eg = item.get(key, "").strip()
        if eg:
            # Remove Chinese part at the end of English examples
            eg_clean = re.sub(r'[\u4e00-\u9fff].*$', '', eg).strip()
            if eg_clean:
                examples.append(eg_clean)
            else:
                examples.append(eg)
    
    if not examples:
        # Default examples for common words
        default_examples = {
            "garrulous": "The garrulous speaker talked for hours without letting anyone else speak.",
            "flippancy": "His flippancy during the serious meeting offended many colleagues.",
            "fretful": "The fretful baby kept crying throughout the long flight.",
            "flout": "Some drivers repeatedly flout traffic regulations without any concern.",
            "flounder": "The inexperienced manager began to flounder when faced with unexpected challenges.",
            "fulminate": "The editorial continued to fulminate against the government's policies.",
            "gainsay": "No one could gainsay the undeniable evidence presented in court.",
            "gambol": "The lambs gamboled happily across the spring meadow.",
            "garble": "The witness's testimony was garbled by poor translation.",
            "gild": "Critics accused the author of trying to gild a mediocre story with fancy prose.",
            "gibe": "The opposing candidate continued to gibe at his rival's record.",
            "gloat": "It is ungracious to gloat over a defeated opponent.",
            "goggle": "The tourists goggled at the magnificent architecture of the cathedral.",
            "goldbrick": "He was known as a goldbrick who always avoided difficult assignments.",
            "gourmand": "The gourmand spent his entire fortune on exotic dining experiences.",
            "gourmet": "She prepared a gourmet meal that impressed all the dinner guests.",
            "grandstand": "The politician tended to grandstand for the cameras rather than address real issues.",
            "gripe": "Employees often gripe about the lack of opportunities for advancement.",
            "grovel": "He refused to grovel before the arrogant dictator for mercy.",
            "grueling": "The marathon was a grueling test of physical and mental endurance.",
            "guzzle": "The truck guzzles fuel at an alarming rate.",
            "hack": "He hired a hack writer to produce cheap articles for the magazine.",
            "hackneyed": "The movie's plot was so hackneyed that the audience predicted every twist.",
            "halcyon": "She often reminisced about the halcyon days of her youth.",
            "half-baked": "The committee rejected the half-baked proposal as impractical.",
            "harangue": "The coach delivered a lengthy harangue about the team's poor performance.",
            "harass": "It is illegal to harass employees based on their gender or race.",
            "harbinger": "The first frost is a harbinger of the approaching winter.",
            "hauteur": "Her natural hauteur made it difficult for her to make friends.",
            "heartrending": "The documentary told a heartrending story of survival against all odds.",
            "hedonism": "Ancient Epicurean philosophy is often misunderstood as mere hedonism.",
            "hegemony": "The nation sought to maintain its hegemony over the entire region.",
            "heinous": "The jury found the defendant guilty of a heinous crime.",
            "heresy": "His unconventional views were considered heresy by the scientific establishment.",
            "hermetic": "The hermetic seal ensured that no air could enter the container.",
            "heterodox": "The professor's heterodox theories challenged the academic establishment.",
            "hidebound": "The hidebound committee refused to adopt any innovative teaching methods.",
            "hie": "The messenger hied himself to the capital with the urgent news.",
            "histrionic": "The actress was known for her histrionic gestures on and off the stage.",
            "hodgepodge": "The essay was a hodgepodge of unrelated ideas without any coherent argument.",
            "homily": "The priest delivered a brief homily on the importance of forgiveness.",
            "homogenize": "Globalization tends to homogenize cultures around the world.",
            "hoodwink": "The fraudulent scheme hoodwinked thousands of unsuspecting investors.",
            "hortative": "The president's hortative speech rallied the nation during the crisis.",
            "hubris": "His failure was ultimately caused by his overwhelming hubris.",
            "hyperbole": "His claim that the project would save the world was pure hyperbole.",
            "hypnotic": "The rhythmic sound of the waves had a hypnotic effect on the listeners.",
            "iconoclast": "The artist was an iconoclast who challenged every artistic convention.",
            "ignominy": "The general resigned in ignominy after the military defeat.",
            "illuminati": "Conspiracy theories often reference the secretive illuminati.",
            "imbroglio": "The diplomatic imbroglio threatened to escalate into an international crisis.",
            "immure": "The writer immured himself in a remote cabin to finish his novel.",
            "impending": "The impending storm forced the sailors to return to the harbor.",
            "impenitent": "The convicted criminal remained impenitent even after sentencing.",
            "imperturbable": "The veteran pilot remained imperturbable during the emergency landing.",
            "importune": "Street vendors would importune passersby to buy their merchandise.",
            "impudent": "The impudent child talked back to the teacher without any remorse.",
            "impugn": "The lawyer sought to impugn the credibility of the prosecution's witness.",
            "impuissance": "The government's impuissance in the crisis frustrated the citizens.",
            "inadvertent": "The scientist made an inadvertent error in the experimental design.",
            "inane": "The reality show was filled with inane comments and trivial conversations.",
            "incandescent": "The incandescent light bulb illuminated the entire room.",
            "incantation": "The witch murmured an ancient incantation under the full moon.",
            "incendiary": "The politician's incendiary remarks sparked widespread protests.",
            "incogitant": "The incogitant driver ran the red light without noticing it.",
            "incontrovertible": "The DNA evidence provided incontrovertible proof of his guilt.",
            "inculpate": "The new evidence served to inculpate the defendant further.",
        }
        
        example = default_examples.get(name, f"The {name} concept is widely discussed in academic circles.")
        examples = [example]
    else:
        # Use curated default if the raw example is too short/trivial
        short_examples = {
            "garrulous": "The garrulous speaker talked for hours without letting anyone else speak.",
            "gainsay": "No one could gainsay the undeniable evidence presented in court.",
            "fickle": "When the family fortune disappeared, so did their fickle friends.",
            "flamboyant": "The flamboyant actor wore an outrageous costume to the award ceremony.",
            "gauche": "It would be extremely gauche to mention the subject at the dinner table.",
            "hermetic": "The hermetic seal on the container prevented any air from entering.",
        }
        best_raw = examples[0]
        if name in short_examples and len(best_raw.split()) < 8:
            examples = [short_examples[name]]
        else:
            # Fix known bad examples
            for i, eg in enumerate(examples):
                # Fix "The Hitler's" -> "Hitler's"
                if "The Hitler" in eg and "The Hitler's" in eg:
                    eg = eg.replace("The Hitler's", "Hitler's")
                elif eg.startswith("The Hitler") and not eg.startswith("The Hitler's"):
                    eg = "Hitler" + eg[len("The Hitler"):]
                examples[i] = eg
    
    best = examples[0]
    
    # Fix sentences starting with lowercase
    if best and best[0].islower():
        best = best[0].upper() + best[1:]
    
    # Add period if missing
    if best and best[-1] not in '.!?。！？':
        best += '.'
    
    # Bold the word with context (2-4 following words)
    name_lower = name.lower()
    best_lower = best.lower()
    
    # Try exact match first, then inflections
    idx = best_lower.find(name_lower)
    word_in_text = name
    
    if idx < 0:
        # Try common inflections
        for suffix in ['s', 'es', 'ed', 'ing', 'er', 'ers', 'ly', 'ness', 'ment', 'tion', 'tions', 'ies']:
            alt = name_lower + suffix
            idx = best_lower.find(alt)
            if idx >= 0:
                word_in_text = best[idx:idx+len(alt)]
                break
        else:
            # Try base form stripping
            for alt_len in range(len(name_lower)-1, max(3, len(name_lower)-3)-1, -1):
                base = name_lower[:alt_len]
                idx = best_lower.find(base)
                if idx >= 0:
                    end = idx + len(base)
                    while end < len(best) and best[end].isalpha():
                        end += 1
                    word_in_text = best[idx:end]
                    idx = best_lower.find(word_in_text.lower())
                    break
    
    if idx >= 0:
        after = best[idx+len(word_in_text):]
        
        # Take next 2-4 words for context (up to ~25 chars)
        after_words = after.split()
        context_after = []
        char_count = 0
        for w in after_words:
            stripped = w.rstrip('.,!?;:')
            if char_count + len(stripped) > 22:
                break
            context_after.append(w)
            if stripped:
                char_count += len(stripped) + 1
            if len(context_after) >= 4:
                break
        
        bold_text = word_in_text
        if context_after:
            bold_text = word_in_text + ' ' + ' '.join(context_after)
        
        # Trim trailing articles/prepositions from bold - keep it tight
        bold_text = re.sub(r'\s+(a|an|the|of|in|on|at|to|for|with|by|from|that|which|who|and|or|but)\s*$', '', bold_text)
        
        end_idx = best.lower().find(bold_text.lower())
        if end_idx >= 0:
            bold_end = end_idx + len(bold_text)
            example = best[:end_idx] + '<b>' + bold_text + '</b>' + best[bold_end:]
        else:
            example = best[:idx] + '<b>' + word_in_text + '</b>' + best[idx+len(name):]
    else:
        example = best
    
    # Truncate to reasonable length if too long
    if len(example) > 150:
        example = example[:147] + '.'
    
    return example


def build_changkao(name, meaning_cn, item, en_meaning):
    """Build changkao field."""
    pos = item.get("pos1", "").strip()
    pos_label = pos.rstrip('.')
    
    # Determine common usage patterns
    patterns = []
    if pos_label in ('adj', 'adv'):
        patterns.append(f"形容词用法")
        # Check for common sentence patterns
        if "not" in en_meaning.lower() or "un" in en_meaning.lower():
            patterns.append("常出现在否定语境中")
    elif pos_label == 'n':
        patterns.append("名词用法")
    elif pos_label == 'v':
        patterns.append("动词用法")
    
    # Determine typical exam context
    exam_contexts = [
        "GRE填空中常见",
    ]
    
    has_ant = item.get("ant1", "").strip() or item.get("ant2", "").strip()
    has_syn = item.get("syn1", "").strip()
    
    if has_ant:
        exam_contexts.append("常考反义对比")
    if has_syn:
        exam_contexts.append("常考同义词群")
    
    # Determine if commonly paired with prepositions
    prep_hints = {
        "impede": "常与from搭配",
        "incite": "常与to搭配",
        "immune": "常与to/from搭配",
        "impose": "常与on/upon搭配",
        "importune": "常与for搭配",
        "impenetrable": "常与to搭配",
        "impervious": "常与to搭配",
        "fetter": "常接by",
        "gibe": "常与at搭配",
        "gloat": "常与over搭配",
        "grieve": "常与for/over搭配",
        "grovel": "常与before/to搭配",
        "gush": "常与over/about搭配",
        "hamper": "常接by",
        "hanker": "常与after/for搭配",
        "harangue": "常与about/at搭配",
        "harbor": "常接against/toward",
        "hew": "常与to搭配",
        "hold": "常与against搭配",
        "hone": "常接skill",
        "imbibe": "直接接宾语",
        "immure": "常接in",
        "impinge": "常与on/upon搭配",
        "implicate": "常接in",
        "import": "常与from搭配",
        "impute": "常与to搭配",
        "incise": "常接in/into",
        "incline": "常与to/toward搭配",
        "indict": "常与for搭配",
        "induce": "常接to",
    }
    
    parts = [f"· 常考：{name}"]
    if patterns:
        parts.append("，".join(patterns) if len(patterns) <= 2 else patterns[0])
    
    if name in prep_hints:
        parts.append(prep_hints[name])
    
    parts.append("，".join(exam_contexts))
    
    return "，".join(p for p in parts if p) + "。"


def build_exam_tips(name, item):
    """Build exam_tips with syn and ant."""
    # Collect all synonyms
    syns_parts = []
    for key in ['syn1', 'syn2']:
        s = item.get(key, "").strip()
        if s:
            clean = clean_syn_ant(s)
            if clean:
                syns_parts.append(clean)
    
    all_syns = ", ".join(p for p in syns_parts if p)
    # Limit to reasonable number
    syn_list = [s.strip() for s in all_syns.replace(", ", ",").split(",") if s.strip()]
    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for s in syn_list:
        if s.lower() not in seen:
            seen.add(s.lower())
            deduped.append(s)
    all_syns = ", ".join(deduped[:12])  # max 12 synonyms
    
    # Collect antonyms
    ants_parts = []
    for key in ['ant1', 'ant2']:
        a = item.get(key, "").strip()
        if a:
            clean = clean_syn_ant(a)
            if clean:
                ants_parts.append(clean)
    
    # Add extra antonyms from our curated list
    if name in EXTRA_ANTS:
        extra = clean_syn_ant(EXTRA_ANTS[name])
        if extra:
            ants_parts.append(extra)
    # Also check with pos
    for key in [f"{name}(n)", f"{name}(v)", f"{name}(adj)", f"{name}(adv)"]:
        if key in EXTRA_ANTS:
            extra = clean_syn_ant(EXTRA_ANTS[key])
            if extra:
                ants_parts.append(extra)
    
    all_ants = ", ".join(p for p in ants_parts if p)
    ant_list = [a.strip() for a in all_ants.replace(", ", ",").split(",") if a.strip()]
    seen_ant = set()
    deduped_ant = []
    for a in ant_list:
        if a.lower() not in seen_ant:
            seen_ant.add(a.lower())
            deduped_ant.append(a)
    all_ants = ", ".join(deduped_ant[:12])  # max 12 antonyms
    
    if not all_syns:
        all_syns = "（GRE常考同义，请补充）"
    if not all_ants:
        all_ants = "（GRE常考反义，请补充）"
    
    return f"💡同义：{all_syns} | 反义：{all_ants}"


# ===== MAIN PROCESSING =====
results = []

for item in data:
    name = item["name"]
    
    # --- meaning_cn ---
    pos1 = item.get("pos1", "").strip()
    meaning1 = item.get("meaning1", "").strip()
    pos2 = item.get("pos2", "").strip()
    meaning2 = item.get("meaning2", "").strip()
    
    cn1 = extract_cn(meaning1)
    en_meaning = extract_en(meaning1)
    
    meanings = []
    if cn1:
        meanings.append((pos1, cn1))
    
    if pos2 and meaning2:
        cn2 = extract_cn(meaning2)
        if cn2 and cn2 != cn1:
            meanings.append((pos2, cn2))
    
    if not meanings:
        meanings.append((pos1, name))
    
    # Check for duplicate pos prefix in second meaning
    if len(meanings) >= 2 and meanings[0][0] == meanings[1][0]:
        meaning_cn = f"{meanings[0][0]}{meanings[0][1]}；{meanings[1][1]}"
    elif len(meanings) == 1:
        meaning_cn = f"{meanings[0][0]}{meanings[0][1]}"
    else:
        meaning_cn = f"{meanings[0][0]}{meanings[0][1]}；{meanings[1][0]}{meanings[1][1]}"
    
    # --- memo ---
    memo = ROOTS.get(name, f"⭐词根：{name}")
    
    # --- example ---
    example = build_example(name, item)
    
    # --- changkao ---
    changkao = build_changkao(name, meaning_cn, item, en_meaning)
    
    # --- exam_tips ---
    exam_tips = build_exam_tips(name, item)
    
    results.append({
        "name": name,
        "meaning_cn": meaning_cn,
        "memo": memo,
        "example": example,
        "changkao": changkao,
        "exam_tips": exam_tips
    })

# Write output
with open('/home/Lu/gre_batch_4_done.json', 'w', encoding='utf-8') as f:
    for item in results:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f"✅ Processed {len(results)} entries")
print(f"✅ Output: /home/Lu/gre_batch_4_done.json")

# Print samples
for sample_name in ['fetid', 'fetter', 'fiasco', 'indifferent', 'flourish', 'garrulous', 'impeccable']:
    for r in results:
        if r['name'] == sample_name:
            print(f"\n--- {sample_name} ---")
            print(json.dumps(r, ensure_ascii=False, indent=2))
            break
