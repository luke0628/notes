#!/usr/bin/env python3
"""Process GRE batch 8: savvy → tawdry (306 words).
Improved version with comprehensive root analysis and robust example/synonym handling.
"""

import json
import re
import sys

# ─────────────────────────────────────────────
# 1. Comprehensive root database (306 words)
# ─────────────────────────────────────────────
ROOTS = {
    'savvy': 'sav-知道 + y → 知识、智慧',
    'scads': 'scad-大量 + s → 大量',
    'scant': 'scant-不足 → 缺乏的',
    'scathing': 'scathe-伤害 + ing → 严厉的、尖刻的',
    'schism': 'schis-分裂 + m → 分裂、分歧',
    'scintillate': 'scintill-火花 + ate → 发出火花、闪耀',
    'scion': 'sci-知道 + on → 子孙（知晓家族血脉者）',
    'scission': 'sciss-切割 + ion → 切断、分裂',
    'scoff': 'scoff-嘲弄 → 嘲笑；狼吞虎咽',
    'scorch': 'scorch-烧焦 → 炙烤、烘干',
    'scorn': 'scorn-轻蔑 → 鄙视、不屑',
    'scotch': 'scotch-划伤→阻止 → 制止、粉碎（谣言）',
    'scour': 'scour-擦洗 → 用力擦洗；搜查',
    'scowl': 'scowl-皱眉 → 怒视、皱眉',
    'scrappy': 'scrap-碎片 + py → 好斗的（如碎片般尖锐）',
    'scrap': 'scrap-碎片 → 废料；抛弃',
    'scrawl': 'scrawl-潦草 → 乱涂、潦草地写',
    'scribble': 'scrib-写 + ble → 潦草地书写',
    'scruple': 'scrup-谨慎 + le → 顾虑、顾忌',
    'scrupulous': 'scrup-谨慎 + ulous → 审慎的、一丝不苟的',
    'scrutable': 'scrut-检查 + able → 可以理解的',
    'scrutinize': 'scrut-检查 + inize → 仔细检查、细察',
    'scuff': 'scuff-磨损 → 磨损；拖步走',
    'scurrilous': 'scurril-粗俗 + ous → 说粗话的、辱骂的',
    'scurvy': 'scurv-坏血病 + y → 下流的、卑鄙的',
    'seamy': 'seam-缝合 + y → 肮脏的（指衣服内缝未处理的一面）',
    'secluded': 'se-分开 + clud-关闭 + ed → 隐僻的、隐蔽的',
    'secrete': 'se-分开 + cret-产生 + e → 分泌；隐藏',
    'sedate': 'sed-坐 + ate → 淡定的、安静的（稳坐不动）',
    'sedentary': 'sed-坐 + entary → 久坐的、固定不动的',
    'seduce': 'se-离去 + duc-引导 + e → 诱使…偏离正道',
    'sedulous': 'sed-坐 + ulous → 勤勉的（坐得住）',
    'seemly': 'seem-看起来 + ly → 得体的、合适的',
    'seep': 'seep-渗 → 渗出、渗漏',
    'seethe': 'seeth-沸腾 + e → 沸腾、激动',
    'segment': 'seg-切割 + ment → 部分、片段',
    'seismic': 'seism-地震 + ic → 地震的；重大的',
    'seminal': 'semin-种子 + al → 开创性的、影响深远的',
    'sensory': 'sens-感觉 + ory → 感官的',
    'sentient': 'senti-感觉 + ent → 有知觉力的',
    'sequester': 'sequ-跟随 + ster → 使隔离、使隐退',
    'serendipity': 'serendip-意外 + ity → 意外发现的乐趣',
    'serene': 'seren-平静 + e → 宁静的、平静的',
    'serpentine': 'serpent-蛇 + ine → 蜿蜒的、曲折的',
    'servile': 'serv-奴仆 + ile → 奴性的、卑躬屈膝的',
    'sever': 'sever-切断 → 切断、断绝',
    'shard': 'shard-碎片 → （陶瓷、玻璃）碎片',
    'sheathe': 'sheath-鞘 + e → 插入鞘、包裹',
    'sheer': 'sheer-完全的 → 纯粹的、陡峭的',
    'shirk': 'shirk-逃避 → 逃避（责任、义务）',
    'shrewd': 'shrewd-精明 → 精明的、敏锐的',
    'shun': 'shun-避开 → 回避、避免',
    'sift': 'sift-筛 → 筛选、细查',
    'simper': 'simper-傻笑 → 傻笑、假笑',
    'simulate': 'simul-相似 + ate → 模拟、假装',
    'sinecure': 'sine-无 + cur-照顾 + e → 闲职、挂名职务',
    'singular': 'singul-单独 + ar → 独特的；非凡的',
    'sinuous': 'sinu-弯曲 + ous → 蜿蜒的、迂回的',
    'skeptic': 'skept-怀疑 + ic → 怀疑论者',
    'skimp': 'skimp-节省 → 吝啬、少给',
    'skirt': 'skirt-裙子（边缘）→ 绕过、回避',
    'skittish': 'skitt-易惊 + ish → 易激动的、轻浮的',
    'slack': 'slack-松弛 → 松懈的、松散的',
    'slander': 'sland-诽谤 + er → 口头诽谤、诋毁',
    'slate': 'slate-石板 → 预定；严厉批评',
    'sleek': 'sleek-光滑 → 光滑的、时髦的',
    'sleight': 'sleight-巧妙 → 巧妙手法、灵巧',
    'slogan': 'slog-战斗 + an → 标语、口号',
    'slot': 'slot-狭槽 → 放入狭槽；安排位置',
    'slothful': 'sloth-懒惰 + ful → 懒惰的、怠惰的',
    'sluggish': 'slugg-缓慢 + ish → 缓慢的、迟钝的',
    'slumber': 'slumber-睡眠 → 睡眠、沉睡',
    'smear': 'smear-涂抹 → 涂抹；诽谤、诋毁',
    'smelt': 'smelt-熔炼 → 熔炼、提炼',
    'smirk': 'smirk-假笑 → 得意地笑、假笑',
    'smother': 'smother-窒息 → 使窒息；压制',
    'smug': 'smug-自满 → 自满的、沾沾自喜的',
    'snare': 'snare-陷阱 → 陷阱、圈套',
    'snub': 'snub-冷落 → 冷落、怠慢',
    'soak': 'soak-浸泡 → 浸泡；吸收',
    'sober': 'sober-清醒 → 清醒的；朴素的',
    'solicit': 'soli-全部 + cit-唤起 → 恳求；拉客',
    'solicitous': 'solicit-关心 + ous → 热切关心的、挂念的',
    'somnolent': 'somn-睡眠 + olent → 困倦的、催眠的',
    'sonorous': 'son-声音 + orous → 洪亮的、响亮的',
    'soothe': 'sooth-真实 + e → 安慰、抚慰',
    'sophist': 'soph-智慧 + ist → 诡辩家',
    'sophisticated': 'soph-智慧 + isticated → 复杂的、老练的',
    'soporific': 'sopor-睡眠 + ific → 催眠的、困倦的',
    'sordid': 'sord-肮脏 + id → 肮脏的、卑鄙的',
    'sparse': 'spars-散开 + e → 稀疏的、稀少的',
    'spartan': 'Spartan-斯巴达 → 简朴的、艰苦的',
    'spasmodic': 'spasm-痉挛 + odic → 痉挛的、间歇性的',
    'spatial': 'spati-空间 + al → 空间的',
    'spawn': 'spawn-产卵 → 产卵；大量产生',
    'specious': 'speci-外观 + ous → 似是而非的、华而不实的',
    'spectrum': 'spect-看 + rum → 光谱；范围',
    'spendthrift': 'spend-花费 + thrift-节约 → 挥霍者、败家子',
    'spirited': 'spirit-精神 + ed → 精神饱满的、热烈的',
    'splendid': 'splend-发光 + id → 辉煌的、极好的',
    'splice': 'splice-编织 → 拼接、接合',
    'spontaneous': 'spont-自愿 + aneous → 自发的、自然的',
    'sporadic': 'sporad-分散 + ic → 偶发的、零星的',
    'sprightly': 'spright-精灵 + ly → 活泼的、精力充沛的',
    'spur': 'spur-马刺 → 激励、刺激',
    'spurious': 'spuri-虚假 + ous → 虚假的、伪造的',
    'squalid': 'squal-肮脏 + id → 肮脏的、恶劣的',
    'stagnate': 'stagn-池塘 + ate → 停滞、不发展',
    'stale': 'stale-陈旧 → 陈腐的、不新鲜的',
    'stalwart': 'stal-坚固 + wart → 坚定的、忠诚的',
    'stamina': 'stam-站立 + ina → 耐力、持久力',
    'staple': 'staple-主要 → 主要的； staples 订书钉',
    'stark': 'stark-完全的 → 完全的；荒凉的',
    'static': 'stat-站立 + ic → 静止的、静态的',
    'steadfast': 'stead-稳定 + fast-牢固 → 坚定的、不动摇的',
    'steep': 'steep-陡峭 → 陡峭的；（价格）过高的；浸泡',
    'stellar': 'stell-星星 + ar → 星的；杰出的',
    'stem': 'stem-茎 → 阻止；起源于',
    'stereotype': 'stereo-固定 + type-类型 → 刻板印象',
    'sterile': 'ster-无菌 + ile → 无菌的；贫瘠的；缺乏新意的',
    'stifle': 'stifl-窒息 + e → 窒息、抑制',
    'stigma': 'stigm-刺 + a → 耻辱、污名',
    'stint': 'stint-限制 → 节省；定额工作',
    'stipulate': 'stipul-要求 + ate → 规定、明确要求',
    'stock': 'stock-库存 → 库存的；陈旧的；惯用的',
    'stodgy': 'stodge-浓稠食物 + y → 乏味的、古板的',
    'stolid': 'stol-迟钝 + id → 冷漠的、无动于衷的',
    'stratify': 'strati-层次 + fy → 分层、阶层化',
    'stride': 'stride-大步 → 大步走、跨越',
    'stringent': 'string-拉紧 + ent → 严格的、严厉的',
    'strive': 'striv-努力 + e → 努力、奋斗',
    'strut': 'strut-支柱 → 趾高气扬地走',
    'stubborn': 'stubborn-顽固 → 顽固的、固执的',
    'studied': 'study-学习 + ed → 精心安排的、刻意的',
    'stultify': 'stult-愚蠢 + ify → 使愚蠢、使无效',
    'stun': 'stun-震惊 → 使震惊、使目瞪口呆',
    'stunt': 'stunt-阻碍 → 阻碍…发育；特技表演',
    'stupefy': 'stup-麻木 + efy → 使惊呆、使目瞪口呆',
    'stupendous': 'stupend-惊人 + ous → 惊人的、了不起的',
    'stymie': 'stymie-阻碍（高尔夫术语）→ 阻碍、妨碍',
    'subdue': 'sub-下 + du-引导 + e → 征服、制服',
    'subjective': 'sub-下 + ject-投 + ive → 主观的',
    'sublime': 'sub-下 + lim-门槛 + e → 崇高的、壮丽的',
    'submerge': 'sub-下 + merg-浸 + e → 淹没、浸没',
    'submissive': 'sub-下 + miss-送 + ive → 顺从的、服从的',
    'subordinate': 'sub-下 + ordin-顺序 + ate → 从属的、下级的',
    'subsequent': 'sub-下 + sequ-跟随 + ent → 随后的、后来的',
    'substantial': 'sub-下 + stant-站立 + ial → 实质的、大量的',
    'substantiate': 'substant-实质 + iate → 证实、证明',
    'substitute': 'sub-下 + stitut-放置 + e → 替代、替换',
    'subsume': 'sub-下 + sum-拿 + e → 包含、纳入',
    'subterfuge': 'subter-下 + fug-逃 + e → 托词、诡计',
    'subtle': 'sub-下 + tle → 微妙的、精细的',
    'subversive': 'sub-下 + vers-转 + ive → 颠覆性的',
    'succinct': 'suc-下 + cinct-捆扎 → 简洁的、简明的',
    'suffocate': 'suf-下 + foc-喉咙 + ate → 窒息、使透不过气',
    'suffrage': 'suffrag-支持 + e → 投票权、选举权',
    'sullen': 'sull-独自 + en → 闷闷不乐的、愠怒的',
    'sumptuous': 'sumpt-消费 + uous → 奢侈的、豪华的',
    'sunder': 'sunder-分开 → 分离、割裂',
    'supercilious': 'super-上 + cili-眉毛 + ous → 傲慢的、目空一切的',
    'superficial': 'super-上 + fic-表面 + ial → 表面的、肤浅的',
    'superfluous': 'super-上 + flu-流 + ous → 多余的、过剩的',
    'supersede': 'super-上 + sed-坐 + e → 取代、替代',
    'supine': 'sup-上 + ine → 仰卧的；懒散的',
    'supplant': 'sup-下 + plant-种植 → 取代、排挤',
    'supple': 'suppl-柔软 + e → 柔软的、灵活的',
    'supplement': 'supple-补充 + ment → 补充、增补',
    'supplicate': 'sup-下 + plic-折叠 + ate → 恳求、哀求',
    'surge': 'surg-升起 + e → 汹涌、激增',
    'surly': 'sur-超越 + ly → 脾气坏的、不友好的',
    'surmount': 'sur-上 + mount-山 → 克服、战胜',
    'surpass': 'sur-上 + pass-通过 → 超越、胜过',
    'surreptitious': 'sur-下 + rept-爬 + itious → 鬼鬼祟祟的、 secret',
    'surrogate': 'sur-下 + rog-要求 + ate → 替代者、代用品',
    'surveillance': 'sur-上 + veill-看 + ance → 监视、监督',
    'susceptible': 'sus-下 + cept-拿 + ible → 易受影响的、敏感的',
    'suspense': 'sus-下 + pens-挂 + e → 悬疑、悬念',
    'sustain': 'sus-下 + tain-保持 → 维持、支撑',
    'swarm': 'swarm-群 → 蜂拥、群集',
    'sway': 'sway-摇摆 → 摇摆；影响、支配',
    'swelter': 'swelter-闷热 → 闷热、热得难受',
    'swerve': 'swerve-转 → 突然转向、偏离方向',
    'swift': 'swift-快速 → 快速的、迅速的',
    'swindle': 'swindl-欺骗 + e → 诈骗、欺诈',
    'sycophant': 'syco-无花果 + phant-显示 → 谄媚者、马屁精',
    'symbiosis': 'sym-共同 + bio-生命 + sis → 共生、互利关系',
    'symptom': 'sym-共同 + ptom-落下 → 症状、征兆',
    'synergic': 'syn-共同 + erg-工作 + ic → 协同的、合作的',
    'synonymous': 'syn-共同 + onym-名字 + ous → 同义的',
    'synopsis': 'syn-共同 + ops-看 + is → 摘要、概要',
    'synthesis': 'syn-共同 + thesis-放置 → 合成、综合',
    'tacit': 'tacit-沉默 → 默许的、心照不宣的',
    'taciturn': 'tacit-沉默 + urn → 沉默寡言的',
    'tackle': 'tackle-装备 → 着手处理、应对',
    'tact': 'tact-触觉 → 机敏、圆滑',
    'tactile': 'tact-触 + ile → 触觉的、能触知的',
    'tactless': 'tact-触觉 + less → 不机智的、笨拙的',
    'talisman': 'talisman-护符 → 护身符、辟邪物',
    'taint': 'taint-玷污 → 污染、玷污',
    'tamper': 'tamper-干扰 → 篡改、干预',
    'tangent': 'tang-接触 + ent → 离题（离开正题）；切线',
    'tangible': 'tang-触 + ible → 可触知的、确凿的',
    'tangy': 'tang-尖刺 + y → 味道刺激的',
    'tantalize': 'Tantalus-坦塔罗斯（希腊神话）→ 挑逗、引诱',
    'tantamount': 'tant-同等 + amount → 等价的、相当于',
    'tantrum': 'tantrum-发脾气 → 勃然大怒',
    'taper': 'taper-蜡烛渐变细 → 逐渐变细；减少',
    'tardy': 'tard-慢 + y → 迟缓的、迟到的',
    'tarnish': 'tarn-暗淡 + ish → 失去光泽、玷污',
    'tasteful': 'taste-品味 + ful → 有品位的、雅致的',
    'tasty': 'taste-味道 + y → 美味的、可口的',
    'tatty': 'tatty-破旧 → 破旧的、褴褛的',
    'taunt': 'taunt-嘲弄 → 嘲弄、挑衅',
    'taut': 'taut-绷紧 → 紧绷的；整洁的',
    'tawdry': 'tawdry-俗丽 → 俗气的、花哨而廉价的',
    'self-abasement': 'self-自己 + abase-贬低 + ment → 自卑、自谦',
    'self-absorbed': 'self-自己 + absorb-吸收 + ed → 自恋的、自私的',
    'sensation': 'sens-感觉 + ation → 感觉、知觉',
    'sensitive': 'sens-感觉 + itive → 敏感的',
    'sentinel': 'sent-感觉 + inel → 哨兵（警觉者）',
    'septic': 'sept-腐烂 + ic → 腐败的、感染的',
    'sepulchral': 'sepulch-坟墓 + ral → 阴沉的、丧葬的',
    'sequela': 'sequ-跟随 + ela → 结果、后遗症',
    'sere': 'sere-干枯 → 干枯的、凋萎的',
    'sermon': 'serm-讲话 + on → 布道、说教',
    'serrate': 'serr-锯齿 + ate → 锯齿状的',
    'serried': 'serr-锯齿 + ied → 密集的（如锯齿般紧密排列）',
    'severe': 'sever-严厉 + e → 严厉的、严重的',
    'shackle': 'shackle-脚镣 → 束缚、枷锁',
    'shadow': 'shadow-影子 → 偷偷尾随',
    'shallow': 'shallow-浅 → 浅显的、浅薄的',
    'sham': 'sham-假装 → 欺瞒、假冒',
    'shiftless': 'shift-改变 + less-无 → 胸无大志的、懒惰的',
    'shipshape': 'ship-船 + shape-形状 → 井然有序的（船上的整洁状态）',
    'shoal': 'shoal-浅 → 浅的；鱼群',
    'shopworn': 'shop-商店 + worn-磨损 → 陈旧的、过时的',
    'shred': 'shred-碎片 → 少量、碎条',
    'shrink': 'shrink-收缩 → 缩小、退缩',
    'shroud': 'shroud-裹尸布 → 隐蔽物、覆盖',
    'shrug': 'shrug-耸肩 → 轻视、忽略',
    'sidestep': 'side-旁边 + step-步 → 回避、侧步躲避',
    'signal': 'sign-标记 + al → 显著的、非同寻常的',
    'simpleton': 'simple-简单 + ton-人 → 笨蛋、头脑简单者',
    'sin': 'sin-罪 → 罪恶的事',
    'sincere': 'sin-无 + cere-蜡 → 真诚的（无蜡的、不掩饰的）',
    'sinew': 'sinew-肌腱 → 活力、力量',
    'singe': 'singe-烧焦 → 轻微烧焦',
    'sip': 'sip-小口喝 → 啜饮',
    'skeleton': 'skeleton-骨架 → 框架、梗概',
    'skirmish': 'skirmish-小冲突 → 小规模战斗',
    'slake': 'slake-缓和 → 使满足、解渴',
    'slant': 'slant-倾斜 → 角度、偏向性的看法',
    'slew': 'slew-大量 → 许多、大量',
    'slight': 'slight-轻微 → 不重要的、纤细的',
    'sling': 'sling-投掷 → 投掷、扔',
    'slippery': 'slip-滑 + pery → 光滑的、不可靠的',
    'slipshod': 'slip-滑 + shod-穿鞋 → 粗心的、不严谨的',
    'sloppy': 'slop-溅出 + py → 邋遢的、马虎的',
    'sloth': 'sloth-懒惰 → 怠惰、懒散',
    'slouch': 'slouch-没精打采 → 懒人、低头垂肩',
    'slovenly': 'sloven-邋遢鬼 + ly → 邋遢的、不修边幅的',
    'sluggard': 'slugg-缓慢 + ard-人 → 懒人、怠惰者',
    'slur': 'slur-含糊 → 耻辱（含糊不清的指责）',
    'sly': 'sly-狡猾 → 狡猾的、诡秘的',
    'smarmy': 'smarm-讨好 + y → 虚情假意的、谄媚的',
    'smart': 'smart-锐利 → 聪颖的、反应敏捷的',
    'smattering': 'smatter-一知半解 + ing → 浅薄的知识',
    'smuggling': 'smuggle-走私 + ing → 走私、私运',
    'snarl': 'snarl-纠缠 → 纠结、混乱',
    'sneer': 'sneer-嘲笑 → 轻蔑地嘲笑',
    'snobbish': 'snob-势利 + bish → 谄上傲下的、自大的',
    'sodden': 'sod-浸泡 + en → 湿透的',
    'solace': 'sol-安慰 + ace → 安慰、慰藉',
    'solder': 'solder-焊接 → 连接、联合',
    'solemnity': 'solemn-庄严 + ity → 严肃、庄严',
    'solid': 'solid-坚固 → 固态的、坚固的、可靠的',
    'soliloquy': 'sol-独自 + loqu-说 + y → 独白、自言自语',
    'solitude': 'sol-独自 + itude → 孤独、独居',
    'solvent': 'solv-解决 + ent → 有偿付能力的；溶剂',
    'somatic': 'somat-身体 + ic → 肉体的、身体的',
    'somber': 'som-暗 + ber → 昏暗的、忧郁的',
    'somnolence': 'somn-睡眠 + olence → 瞌睡、嗜睡',
    'sonnet': 'son-声音 + net → 十四行诗',
    'sop': 'sop-浸泡 → 安慰物（用来讨好人的东西）',
    'sophism': 'soph-智慧 + ism → 诡辩（看似聪明实则谬误）',
    'sound': 'sound-健全 → 牢固的、健康的、合理的',
    'spat': 'spat-轻拍 → 小争吵',
    'spate': 'spate-洪水 → 突发的洪水；大量',
    'specific': 'spec-看 + ific → 特有的、具体的',
    'speck': 'speck-斑点 → 小点、少量',
    'spectator': 'spect-看 + ator-人 → 旁观者、观众',
    'speculate': 'spec-看 + ulate → 推测、投机',
    'spent': 'spend-花费 + t → 精疲力竭的、用尽的',
    'spindly': 'spindle-纺锤 + y → 细长纤弱的',
    'spiny': 'spin-刺 + y → 多刺的、棘手的',
    'spleen': 'spleen-脾脏（传统认为与怒气相关）→ 怒气、怨恨',
    'spoof': 'spoof-恶搞 → 轻松模仿、戏谑',
    'sprawl': 'sprawl-伸展 → 杂乱无序地扩展',
    'spurn': 'spurn-踢开 → 摈弃、拒绝',
    'squabble': 'squabble-争吵 → 口角、小争吵',
    'squall': 'squall-尖叫 → 暴风；大声哭喊',
    'squander': 'squander-分散 → 挥霍、浪费',
    'squat': 'squat-蹲 → 矮胖的、蹲着的',
    'squelch': 'squelch-压碎 → 压制、镇压',
    'squint': 'squint-斜视 → 斜视、眯眼看',
    'stabilize': 'stabil-稳定 + ize → 使稳定',
    'stammer': 'stammer-口吃 → 结巴、口吃',
    'startle': 'start-惊起 + le → 使吓一跳',
    'stature': 'stat-站立 + ure → 身高、声望',
    'stealth': 'stealth-秘密 → 秘密行动、隐秘',
    'stench': 'stench-恶臭 → 臭气',
    'stentorian': 'Stentor-（希腊传令官）+ ian → 声音洪亮的',
    'stickler': 'stick-坚持 + ler-人 → 坚持细节者、一丝不苟的人',
    'stiff': 'stiff-僵硬 → 僵硬的、生硬的',
    'stingy': 'sting-刺 + y → 吝啬的（像被刺一样小气）',
    'stipple': 'stippl-点 + e → 点刻、画点',
    'stitch': 'stitch-针脚 → 突然剧痛（像被针刺）',
    'stockade': 'stock-木桩 + ade → 栅栏、围栏',
    'stoic': 'Stoic-斯多葛学派 → 隐忍的、冷静的',
    'stoke': 'stoke-添柴 → 添加燃料、煽动',
    'stomach': 'stomach-胃 → 容忍、忍受',
    'stonewall': 'stone-石头 + wall-墙 → 拒绝合作、阻挠',
    'stouthearted': 'stout-结实 + heart-心 + ed → 勇敢的、刚毅的',
    'strait': 'strait-狭窄 → 海峡；困境',
    'strand': 'strand-线 → 一股、一缕；使搁浅',
    'stratagem': 'strata-策略 + gem → 谋略、策略',
    'stray': 'stray-偏离 → 走失的、漫无目的的',
    'strength': 'strength-力量 → 力量、优势',
    'striate': 'stri-条纹 + ate → 加条纹、有纹路',
    'stricture': 'strict-严格 + ure → 苛评、责难；约束',
    'strident': 'strid-刺耳 + ent → 刺耳的、尖锐的',
    'strike': 'strike-打 → 罢工；攻击；突然想到',
    'strip': 'strip-剥夺 → 脱衣、剥去、剥夺',
    'studio': 'stud-学习 + io → 工作室、画室',
    'stupor': 'stup-麻木 + or → 迟钝、昏迷',
    'sturdy': 'sturdy-结实 → 强健的、结实的',
    'stygian': 'Styx-冥河 + ian → 极黑暗的、地狱般的',
    'subject': 'sub-下 + ject-投 → 臣民；主题；使遭受',
    'subjugate': 'sub-下 + jug-轭 + ate → 征服、镇压',
    'subliminal': 'sub-下 + limin-门槛 + al → 下意识的、潜意识的',
    'subservient': 'sub-下 + serv-服务 + ient → 屈从的、奉承的',
    'subside': 'sub-下 + sid-坐 + e → 下陷、消退、平息',
    'subsidiary': 'sub-下 + sid-坐 + iary → 辅助的、次要的',
    'subsidy': 'sub-下 + sid-坐 + y → 补助金（从下支持）',
    'substantive': 'sub-下 + stant-站立 + ive → 实质的、独立存在的',
    'subvert': 'sub-下 + vert-转 → 颠覆、暗中破坏',
    'succor': 'suc-下 + cor-跑 → 救援、援助',
    'suffuse': 'suf-下 + fus-流 + e → 弥漫、充满',
    'sulk': 'sulk-愠怒 → 生气、闷闷不乐',
    'summary': 'summ-总和 + ary → 摘要、概要',
    'summit': 'summ-最高 + it → 顶点、峰会',
    'summon': 'sum-下 + mon-提醒 → 召集、召唤',
    'superimpose': 'super-上 + impose-强加 → 叠加、添加上去',
    'supposition': 'sup-下 + posit-放 + ion → 假定、推测',
    'suppress': 'sup-下 + press-压 → 压制、抑制',
    'surcharge': 'sur-上 + charge-收费 → 过高收费、附加费',
    'surfeit': 'sur-上 + feit-做 → 过量、饮食过度',
    'surrender': 'sur-上 + render-交出 → 投降、放弃',
    'susceptibility': 'sus-下 + cept-拿 + ibility → 易感性、敏感性',
    'suspend': 'sus-下 + pend-挂 → 暂停、悬挂',
    'suture': 'sut-缝 + ure → 缝合、缝线',
    'svelte': 'svelte-苗条 → (女子)苗条优雅的',
    'swagger': 'swagger-大摇大摆 → 趾高气昂地走',
    'swear': 'swear-发誓 → 咒骂；宣誓',
    'sweltering': 'swelter-闷热 + ing → 酷热的',
    'swill': 'swill-冲洗 → 痛饮、大口吃喝',
    'sybarite': 'Sybaris-（古希腊奢侈城市）→ 奢侈逸乐者',
    'syllabus': 'syl-共同 + lab-拿 + us → 提纲、摘要',
    'syllogism': 'syl-共同 + log-推理 + ism → 三段论、演绎推理',
    'symmetry': 'sym-共同 + metr-测量 + y → 对称、匀称',
    'synchronous': 'syn-共同 + chron-时间 + ous → 同时的、同步的',
}

# ─────────────────────────────────────────────
# 2. Helper functions
# ─────────────────────────────────────────────
def clean_meaning(meaning):
    """Remove English explanation after colon, keep only Chinese meaning."""
    if not meaning:
        return ''
    if ':' in meaning:
        return meaning.split(':')[0].strip()
    if '：' in meaning:
        return meaning.split('：')[0].strip()
    return meaning.strip()

def split_meanings(d):
    """Get up to 2 core meanings from pos1+meaning1 (and pos2 if available)."""
    meanings = []
    if d['pos1'] and d['meaning1']:
        cn = clean_meaning(d['meaning1'])
        pos = d['pos1'].strip()
        # Remove trailing punctuation like "，"
        cn = cn.rstrip('，, ')
        meanings.append(f"{pos}{cn}")
    if d['pos2'] and d['meaning2'] and len(meanings) < 2:
        cn2 = clean_meaning(d['meaning2'])
        pos2 = d['pos2'].strip()
        cn2 = cn2.rstrip('，, ')
        second = f"{pos2}{cn2}"
        if second not in meanings:
            meanings.append(second)
    # If still only 1 meaning, try pos3
    if len(meanings) < 2 and d['pos3'] and d['meaning3']:
        cn3 = clean_meaning(d['meaning3'])
        pos3 = d['pos3'].strip()
        cn3 = cn3.rstrip('，, ')
        third = f"{pos3}{cn3}"
        if third not in meanings:
            meanings.append(third)
    if not meanings:
        return "待补充"
    return " / ".join(meanings[:2])

def build_memo(name):
    """Build root-based memo."""
    key = name.lower()
    if key in ROOTS:
        return f"⭐词根：{ROOTS[key]}"
    return f"⭐词根：{name}-（待考据）→ 待补充核心义"

def extract_english_from_eg(eg_text):
    """Extract the English part from an example string (before Chinese characters)."""
    if not eg_text:
        return ''
    # Find where Chinese starts
    m = re.match(r'^([a-zA-Z0-9\s\'\",\.\-\!\?\(\)\/\:\;\&\#\@\$\%\*\+\=\[\]\{\}\|\\\`\~]+)', eg_text)
    if m:
        return m.group(1).strip()
    # If no clean English prefix, try to remove Chinese characters
    cleaned = re.sub(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef，。、；：""''（）【】《》？！…—·]+', '', eg_text).strip()
    return cleaned

def build_example(name, d):
    """Build a 15-20 word complete English sentence using example material."""
    name_lower = name.lower()
    name_cap = name.capitalize()
    
    # Collect all available examples
    raw_egs = []
    for i in ['1', '2', '3']:
        eg = d.get(f'eg{i}', '')
        if eg:
            raw_egs.append(eg)
    
    if not raw_egs:
        return f"The concept of <b>{name}</b> is central to understanding the passage."
    
    # Try each example to build a good sentence
    for raw_eg in raw_egs:
        eng = extract_english_from_eg(raw_eg)
        if not eng:
            continue
        
        # Ensure good length
        words = eng.split()
        if len(words) < 3:
            continue
        
        # Capitalize first letter
        eng = eng[0].upper() + eng[1:] if eng else eng
        # Ensure period at end
        if eng and not eng[-1] in '.!?':
            eng += '.'
        
        # Check if word is already bolded
        if f'<b>{name_lower}' in eng.lower() or f'<b>{name_cap}' in eng:
            return eng
        
        # Find the word in the sentence
        pattern = re.compile(re.escape(name_lower), re.IGNORECASE)
        matches = list(pattern.finditer(eng))
        
        if matches:
            # Use the first match
            m = matches[0]
            start = m.start()
            end = m.end()
            # Bold: word + up to 3 following words for context
            after = eng[end:]
            after_words = after.split()
            n_context = min(3, len(after_words))
            bold_end = end
            if n_context > 0:
                context_str = ' '.join(after_words[:n_context])
                bold_end = end + len(context_str) + (1 if after and after[0] != ' ' else 0)
            eng_result = eng[:start] + '<b>' + eng[start:bold_end] + '</b>' + eng[bold_end:]
            if 12 <= len(eng_result.split()) <= 25:
                return eng_result
            # If length is off, still return a reasonable version
            return eng_result
    
    # Fallback: just use first sentence with the word bolded
    if raw_egs:
        eng = extract_english_from_eg(raw_egs[0])
        if eng:
            eng = eng[0].upper() + eng[1:] if eng else eng
            if eng and not eng[-1] in '.!?':
                eng += '.'
            # Bold just the word
            pattern = re.compile(re.escape(name_lower), re.IGNORECASE)
            eng = pattern.sub(f'<b>{name}</b>', eng, count=1)
            return eng
    
    return f"The <b>{name}</b> is an important concept to understand."

def parse_synonyms(d):
    """Parse synonyms from syn1/syn2/syn3, returning clean list."""
    all_syns = []
    seen = set()
    for key in ['syn1', 'syn2', 'syn3']:
        raw = d.get(key, '')
        if not raw:
            continue
        # Remove Chinese characters
        clean = re.sub(r'[\u4e00-\u9fff]+', '', raw)
        # Split by comma
        items = [x.strip().rstrip('.,; ') for x in clean.split(',') if x.strip()]
        for item in items:
            # Filter out non-word artifacts
            item_clean = re.sub(r'[^a-zA-Z\-\'\s]', '', item).strip()
            if item_clean and len(item_clean) > 1 and item_clean.lower() not in seen:
                seen.add(item_clean.lower())
                all_syns.append(item_clean)
    return all_syns[:5]

def parse_antonyms(d):
    """Parse antonyms from ant1/ant2/ant3, returning clean list."""
    all_ants = []
    seen = set()
    for key in ['ant1', 'ant2', 'ant3']:
        raw = d.get(key, '')
        if not raw:
            continue
        # Remove Chinese characters
        clean = re.sub(r'[\u4e00-\u9fff]+', '', raw)
        # Split by comma
        items = [x.strip().rstrip('.,; ') for x in clean.split(',') if x.strip()]
        for item in items:
            item_clean = re.sub(r'[^a-zA-Z\-\'\s]', '', item).strip()
            if item_clean and len(item_clean) > 1 and item_clean.lower() not in seen:
                seen.add(item_clean.lower())
                all_ants.append(item_clean)
    return all_ants[:5]

def extract_collocations(name, d):
    """Extract meaningful collocations from examples."""
    collocs = []
    seen = set()
    name_lower = name.lower()
    
    for i in ['1', '2', '3']:
        eg = d.get(f'eg{i}', '')
        if not eg:
            continue
        eng = extract_english_from_eg(eg)
        if not eng:
            continue
        # Find phrases where the word appears + following word(s)
        # Pattern: word followed by up to 2 words
        for m in re.finditer(re.escape(name_lower) + r'\s+(\w+\s*\w*)', eng, re.IGNORECASE):
            phrase = m.group(0).strip().lower()
            if phrase not in seen:
                seen.add(phrase)
                collocs.append(phrase)
        # Also find: word preceded by a word
        for m in re.finditer(r'(\w+)\s+' + re.escape(name_lower), eng, re.IGNORECASE):
            phrase = m.group(0).strip().lower()
            if phrase not in seen:
                seen.add(phrase)
                collocs.append(phrase)
        # Also just the word itself with a common prep/particle
        for m in re.finditer(re.escape(name_lower) + r'\s+(to|of|with|in|for|at|by|from|on|as|the|a|an)', eng, re.IGNORECASE):
            phrase = m.group(0).strip().lower()
            if phrase not in seen:
                seen.add(phrase)
                collocs.append(phrase)
    
    # Deduplicate and limit
    unique = []
    for c in collocs:
        if c not in unique:
            unique.append(c)
    
    return unique[:3]

def build_changkao(name, d):
    """Build changkao with specific collocations + synonym/antonym relationships."""
    collocs = extract_collocations(name, d)
    syns = parse_synonyms(d)
    ants = parse_antonyms(d)
    
    meaning_cn = clean_meaning(d.get('meaning1', ''))
    
    # Build collocation string
    if collocs:
        # Use the first meaningful collocation
        colloc_str = ', '.join(collocs[:2])
    else:
        colloc_str = name
    
    syn_str = ', '.join(syns[:4]) if syns else '待补充'
    ant_str = ', '.join(ants[:4]) if ants else '待补充'
    
    return f"· 常考：{name} 常与 {colloc_str} 搭配（{meaning_cn}），GRE填空中与 {syn_str} 同义，与 {ant_str} 反义"

def build_exam_tips(d):
    """Build exam tips with synonyms and antonyms."""
    syns = parse_synonyms(d)
    ants = parse_antonyms(d)
    
    syn_str = ', '.join(syns[:4]) if syns else '待补充'
    ant_str = ', '.join(ants[:4]) if ants else '待补充'
    
    return f"💡同义：{syn_str} | 反义：{ant_str}"

# ─────────────────────────────────────────────
# 3. Main processing
# ─────────────────────────────────────────────
def process_word(d):
    """Process a single word entry."""
    name = d['name']
    meaning_cn = split_meanings(d)
    memo = build_memo(name)
    example = build_example(name, d)
    changkao = build_changkao(name, d)
    exam_tips = build_exam_tips(d)
    
    return {
        "name": name,
        "meaning_cn": meaning_cn,
        "memo": memo,
        "example": example,
        "changkao": changkao,
        "exam_tips": exam_tips
    }

def main():
    with open('/home/Lu/gre_batch_8_raw.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} entries", file=sys.stderr)
    
    with open('/home/Lu/gre_batch_8_done.json', 'w', encoding='utf-8') as out:
        for d in data:
            result = process_word(d)
            out.write(json.dumps(result, ensure_ascii=False) + '\n')
    
    # Verify
    with open('/home/Lu/gre_batch_8_done.json', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f"Written {len(lines)} lines to /home/Lu/gre_batch_8_done.json", file=sys.stderr)
    
    # Check for "待考据" entries
    pending = 0
    for line in lines:
        if '待考据' in line:
            pending += 1
    print(f"Entries with 待考据: {pending}", file=sys.stderr)
    
    # Check for "待补充" in syn/ant
    pending2 = 0
    for line in lines:
        d = json.loads(line)
        if '待补充' in d['changkao'] or '待补充' in d['exam_tips']:
            pending2 += 1
    print(f"Entries with 待补充 in changkao/exam_tips: {pending2}", file=sys.stderr)

if __name__ == '__main__':
    main()
