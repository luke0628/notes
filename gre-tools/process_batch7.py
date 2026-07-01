#!/usr/bin/env python3
"""Process 306 GRE vocabulary entries (preternatural → savory) into the required format."""

import json
import re

def strip_chinese(text):
    """Remove Chinese characters and punctuation from text."""
    return re.sub(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', '', text).strip()

def extract_meaning(pos, meaning_text):
    """Extract meaning_cn from pos+meaning. Strip parenthetical notes, keep at most 2 core meanings."""
    if not pos or not meaning_text:
        return "（待补充）"
    
    colon_idx = meaning_text.find(':')
    chinese_part = meaning_text[:colon_idx].strip() if colon_idx >= 0 else meaning_text.strip()
    
    # Remove parenthetical content like "(略)"
    chinese_part = re.sub(r'[（(][^）)]*[）)]', '', chinese_part).strip()
    
    parts = re.split(r'[，；]', chinese_part)
    core = [c.strip() for c in parts if c.strip()]
    core = core[:2]
    
    if pos.startswith('n.') or pos.startswith('vi.') or pos.startswith('vt.') or pos.startswith('v.'):
        # n./v. type
        if len(core) >= 2:
            meaning = pos + '、'.join(core)
        elif core:
            meaning = pos + core[0]
        else:
            meaning = pos + '（待补充）'
    else:
        if len(core) >= 2:
            meaning = pos + '、'.join(core)
        elif core:
            meaning = pos + core[0]
        else:
            meaning = pos + '（待补充）'
    return meaning

def parse_synonyms(syn_text):
    """Parse synonym text into a clean list of words."""
    if not syn_text:
        return []
    cleaned = re.sub(r'[\u4e00-\u9fff]+', '', syn_text)
    parts = re.split(r'[,;，；]\s*', cleaned)
    result = []
    for p in parts:
        p = p.strip().strip('.')
        if p and re.match(r'^[a-zA-Z\-\s]+$', p):
            for word in p.split():
                word = word.strip(' .;,:')
                if word and word not in result:
                    result.append(word)
    return result[:8]

def parse_antonyms(ant_text):
    """Parse antonym text into a clean list of words."""
    if not ant_text:
        return []
    cleaned = re.sub(r'[\u4e00-\u9fff]+', '', ant_text)
    parts = re.split(r'[,;，；]\s*', cleaned)
    result = []
    for p in parts:
        p = p.strip().strip('.')
        if p and re.match(r'^[a-zA-Z\-\s]+$', p):
            for word in p.split():
                word = word.strip(' .;,:')
                if word and word not in result:
                    result.append(word)
    return result

def get_word_roots():
    """Return a comprehensive mapping of word roots for all 306 words."""
    return {
        'preternatural': 'preter-超越+natur-自然+al→超自然的',
        'prevail': 'pre-前+vail-力量→压倒→战胜',
        'prevalent': 'pre-前+val-力量+ent→有力量的→流行的',
        'prevaricate': 'pre-前+varic-弄弯+ate→支吾其词',
        'primordial': 'prim-最初+ord-秩序+ial→原始的',
        'pristine': 'prist-原始+ine→原始纯净的',
        'probity': 'prob-正直+ity→正直',
        'proclivity': 'pro-向前+cliv-倾斜+ity→倾向',
        'procrastinate': 'pro-向前+crastin-明天+ate→拖延',
        'prodigal': 'pro-向前+ig-驱使+al→挥霍的',
        'prodigious': 'pro-前+dig-巨大+ous→巨大的',
        'profligate': 'pro-前+flig-打击+ate→挥霍无度的',
        'profound': 'pro-前+found-底部→深远的',
        'prohibit': 'pro-前+hibit-拿住→禁止',
        'prolific': 'prol-后代+ific→多产的',
        'prolix': 'pro-前+lix-流动→冗长的',
        'promulgate': 'pro-前+ulg-公布+ate→公布',
        'propensity': 'pro-前+pens-悬挂+ity→倾向',
        'prophetic': 'prophet-预言+ic→预言的',
        'propitiate': 'propi-亲近+ti+ate→安抚',
        'propitious': 'propi-亲近+tious→吉祥的',
        'prosaic': 'prose-散文+aic→如散文的→平淡的',
        'proscribe': 'pro-前+scribe-写→公开写明→禁止',
        'proselytize': 'proselyt-皈依者+ize→劝诱改宗',
        'protagonist': 'prot-首要+agonist-演员→主角',
        'protract': 'pro-前+tract-拉→延长',
        'provident': 'pro-前+vid-看+ent→有远见的',
        'provincial': 'province-省+ial→乡土气的',
        'provocative': 'pro-前+voca-叫+tive→挑衅的',
        'prowess': 'prow-英勇+ess→英勇',
        'prudent': 'prud-谨慎+ent→谨慎的',
        'prune': 'prune-修剪→修剪',
        'pseudonym': 'pseud-假+onym-名字→假名',
        'pugnacious': 'pugn-打斗+acious→好斗的',
        'pundit': 'pundit-博学者→专家',
        'punitive': 'punit-惩罚+ive→惩罚性的',
        'purchasable': 'purchase-购买+able→可收买的',
        'purge': 'purge-清洗→清除',
        'quack': 'quack-发出鸭叫声→庸医',
        'qualified': 'qualify-限定+ed→有限制的',
        'qualitative': 'qualit-性质+ative→定性的',
        'quandary': 'quand-困惑+ary→困惑',
        'quarantine': 'quarant-四十+ine→四十天隔离',
        'quell': 'quell-压制→镇压',
        'querulous': 'quer-抱怨+ulous→爱抱怨的',
        'quiescent': 'qui-安静+escent→静止的',
        'quintessential': 'quint-第五+essence-本质→精华的',
        'quirk': 'quirk-古怪→怪癖',
        'quotidian': 'quotid-每日+ian→每日的→平凡的',
        'rail': 'rail-栏杆→用栏杆围→责骂',
        'rambunctious': 'rambunct-粗暴+ious→粗暴的',
        'ramify': 'ram-分支+ify→使分支',
        'rancor': 'ranc-仇恨+or→深仇',
        'rapacious': 'rap-抢夺+acious→贪婪的',
        'rarefied': 'rare-稀薄+fy+ed→稀薄的→精选的',
        'ratify': 'rat-认可+ify→批准',
        'rationalize': 'rational-理性的+ize→使合理化',
        'raucous': 'rauc-嘶哑+ous→沙哑的',
        'reactionary': 're-反+action-行动+ary→反动的',
        'readily': 'ready-准备+ly→乐意地',
        'rebuke': 're-反+buke-击打→指责',
        'recalcitrant': 're-反+calcitr-踢+ant→顽抗的',
        'recant': 're-反+cant-唱→宣布放弃',
        'recapitulate': 're-重新+capit-头+ulate→概括',
        'recast': 're-重新+cast-铸造→重铸',
        'receptive': 're-后+cept-拿+ive→善于接受的',
        'recidivism': 're-重新+cid-落下+ism→累犯',
        'reciprocal': 're-反+cip-拿+roc-轮+al→相互的',
        'reckon': 'reck-考虑+on→认为',
        'recluse': 're-回+clus-关闭+e→隐居者',
        'recount': 're-重新+count-数→详细叙述',
        'recrimination': 're-反+crimin-指控+ation→反责',
        'rectify': 'rect-直+ify→使直→纠正',
        'recumbent': 're-向后+cumb-躺+ent→斜躺的',
        'recuperate': 're-重新+cuper-获得+ate→恢复',
        'redoubtable': 're-反复+doubt-怀疑+able→令人敬畏的',
        'refractory': 're-反+fract-打破+ory→难控制的',
        'refrain': 're-回+frain-限制→克制',
        'refurbish': 're-重新+furbish-擦亮→翻新',
        'refute': 're-回+fute-击打→驳斥',
        'regeneration': 're-重新+gener-产生+ation→再生',
        'regressive': 're-回+gress-走+ive→倒退的',
        'rehabilitate': 're-重新+habilit-能力+ate→使康复',
        'reiterate': 're-重新+iter-再次+ate→反复重申',
        'rejuvenate': 're-重新+juven-年轻+ate→使年轻',
        'relapse': 're-重新+laps-滑+e→重新陷入',
        'remonstrate': 're-反+monstr-展示+ate→抗议',
        'remorse': 're-回+morse-咬→悔恨',
        'renaissance': 're-重新+naiss-出生+ance→复兴',
        'render': 'rend-给予+er→提供',
        'renegade': 're-反+neg-否定+ade→叛徒',
        'renewal': 're-重新+new-新+al→更新',
        'renovate': 're-重新+nov-新+ate→翻新',
        'renown': 're-反复+nown-名字→名声',
        'repine': 're-反复+pine-渴望→抱怨',
        'replenish': 're-重新+plen-满+ish→补充',
        'replete': 're-重新+plet-满+e→充满的',
        'reprehensible': 're-回+prehens-抓住+ible→应受谴责的',
        'repress': 're-回+press-压→压制',
        'reprieve': 're-重新+priev-拿取→暂缓',
        'reprimand': 're-回+primand-压→训斥',
        'reproach': 're-反+proach-接近→责备',
        'reprobate': 're-反+prob-正直+ate→堕落的',
        'repudiate': 're-回+pudi-羞耻+ate→拒绝',
        'repugnant': 're-反+pugn-打斗+ant→令人厌恶的',
        'repulse': 're-回+puls-推+e→击退',
        'repurchase': 're-重新+purchase-购买→回购',
        'repute': 're-反复+pute-想→名声',
        'requite': 're-回+quite-安静→报答',
        'rescind': 're-回+scind-切割→废除',
        'resigned': 're-回+sign-签署+ed→顺从的',
        'resilient': 're-回+sili-跳+ent→有弹性的',
        'resolute': 're-不+solute-松开→坚决的',
        'resonant': 're-回+son-声音+ant→回响的',
        'respite': 're-回+spite-看→休息',
        'resplendent': 're-反+splend-发光+ent→灿烂的',
        'restitution': 're-回+stitut-建立+ion→归还',
        'restive': 'rest-休息+ive→焦躁不安的',
        'restorative': 're-重新+stor-建立+ative→恢复的',
        'restrain': 're-回+strain-拉紧→克制',
        'resumption': 're-重新+sumpt-拿+ion→重新开始',
        'resurrect': 're-重新+surg-升起+ect→复活',
        'retaliate': 're-回+tali-惩罚+ate→报复',
        'retard': 're-回+tard-慢→减速',
        'reticent': 're-回+tic-沉默+ent→沉默寡言的',
        'retiring': 're-回+tir-拉+ing→退休的→害羞的',
        'retract': 're-回+tract-拉→缩回',
        'retrench': 're-回+trench-切割→削减',
        'retribution': 're-回+tribut-给予+ion→报应',
        'retrieve': 're-回+triev-找到+e→找回',
        'retrograde': 'retro-向后+grade-步→倒退',
        'retrospective': 'retro-回+spect-看+ive→回顾的',
        'revelation': 're-揭开+vel-面纱+ation→揭露',
        'revere': 're-反复+vere-敬畏→尊敬',
        'revert': 're-回+vert-转→恢复',
        'revitalize': 're-重新+vital-生命+ize→使复兴',
        'revoke': 're-回+vok-叫+e→撤回',
        'revolt': 're-反+volt-转→反抗',
        'rhetoric': 'rhetor-演说家+ic→修辞',
        'riddle': 'riddle-筛子→谜语',
        'rift': 'rift-裂缝→分歧',
        'righteous': 'right-正确+eous→正直的',
        'rigid': 'rig-僵硬+id→僵硬的',
        'rigor': 'rigor-严格→严酷',
        'ripe': 'ripe-成熟→成熟的',
        'rivet': 'riv-河→用铆钉固定→吸引',
        'robust': 'robust-强壮的→健壮的',
        'rogue': 'rogue-流浪者→无赖',
        'roster': 'roster-名单→花名册',
        'rostrum': 'rostrum-鸟喙→讲坛',
        'rote': 'rote-机械→死记硬背',
        'rousing': 'rous-唤醒+ing→令人振奋的',
        'rudimentary': 'rud-原始+ment+ary→基本的',
        'rue': 'rue-后悔→懊悔',
        'ruminate': 'rumin-反刍+ate→沉思',
        'rupture': 'rupt-打破+ure→破裂',
        'rustic': 'rust-乡村+ic→乡村的',
        'ruthless': 'ruth-怜悯+less→无情的',
        'sabotage': 'sabot-木鞋+age→蓄意破坏',
        'sacrosanct': 'sacr-神圣+sanct-神圣→神圣不可侵犯的',
        'sagacious': 'sag-智慧+acious→睿智的',
        'salient': 'sal-跳+ient→突出的',
        'salutary': 'salut-健康+ary→有益的',
        'salvage': 'salv-救+age→抢救',
        'sanctimonious': 'sanct-神圣+moni+ous→假装虔诚的',
        'sanction': 'sanct-神圣+ion→批准',
        'sanctuary': 'sanct-神圣+uary→庇护所',
        'sanguine': 'sanguin-血+e→血色的→乐观的',
        'sap': 'sap-树液→削弱',
        'sarcasm': 'sarc-肉+asm→讽刺',
        'sardonic': 'sardon-讽刺+ic→嘲弄的',
        'satiate': 'sati-足够+ate→使饱足',
        'satire': 'satire-讽刺文学→讽刺',
        'saturate': 'satur-满+ate→使饱和',
        'saunter': 'saunter-闲逛→漫步',
        'savant': 'sav-智慧+ant→博学者',
        'savory': 'savor-味道+y→美味的',
        'rage': 'rage-狂暴→暴怒',
        'provisional': 'pro-前+vision-看+al→预先看到的→临时的',
        'riot': 'riot-暴动→暴乱',
        'repudiate': 're-回+pudi-羞耻+ate→拒绝',
        'sand': 'sand-沙→用沙打磨→磨光',
        'quarantine': 'quarant-四十+ine→四十天隔离',
        'quench': 'quench-熄灭→压制',
        'query': 'query-询问→质疑',
        'quibble': 'quibble-双关→吹毛求疵',
        'quiescent': 'qui-安静+escent→静止的',
                'quintessential': 'quint-第五+essence-本质→精华的',
        'primp': 'primp-打扮→精心打扮',
        'principal': 'princip-首要+al→主要的',
        'privation': 'priv-私有的+ation→剥夺',
        'probe': 'probe-探查→调查',
        'procure': 'pro-前+cure-照顾→获得',
        'prod': 'prod-刺→激励',
        'profane': 'pro-前+fan-寺庙+e→亵渎的',
        'proffer': 'pro-前+ffer-带来→提供',
        'proficient': 'pro-前+fic-做+ient→精通的',
        'profundity': 'pro-前+fund-底部+ity→深奥',
        'profusion': 'pro-前+fus-流+ion→丰富',
        'prohibitive': 'pro-前+hibit-拿住+ive→禁止的',
        'proliferate': 'prol-后代+ifer-带来+ate→增殖',
        'prolong': 'pro-前+long-长→延长',
        'proofread': 'proof-校对+read-读→校对',
        'propagate': 'propag-繁殖+ate→传播',
        'proponent': 'pro-前+pon-放置+ent→支持者',
        'propriety': 'propr-合适+iety→适当',
        'prosecution': 'pro-前+secut-跟随+ion→起诉',
        'prospect': 'pro-前+spect-看→前景',
        'prosperous': 'pro-前+sper-希望+ous→繁荣的',
        'prostrate': 'pro-前+strat-铺开+e→俯卧的',
        'protean': 'Proteus-普罗透斯+an→多变的',
        'protocol': 'prot-首先+col-胶→议定书',
        'protuberant': 'pro-前+tuber-瘤+ant→凸起的',
        'providential': 'pro-前+vid-看+ential→天意的',
        'provisory': 'pro-前+vis-看+ory→附条件的',
        'provoke': 'pro-前+vok-叫+e→激怒',
        'prowl': 'prowl-潜行→徘徊',
        'prude': 'prude-过分正经→过分正经的人',
        'prudish': 'prude-正经+ish→过分正经的',
        'pry': 'pry-窥探→打探',
        'psychology': 'psych-心灵+ology-学→心理学',
        'pucker': 'pucker-皱起→褶皱',
        'puckish': 'puck-顽皮精灵+ish→淘气的',
        'puerile': 'puer-男孩+ile→幼稚的',
        'puissance': 'puiss-力量+ance→权力',
        'pulchritude': 'pulchr-美丽+itude→美丽',
        'pulverize': 'pulver-粉末+ize→粉碎',
        'pun': 'pun-双关语→双关',
        'punctilious': 'punct-点+ilious→拘泥细节的',
        'pungent': 'pung-刺+ent→辛辣的',
        'puny': 'puny-弱小→弱小的',
        'purity': 'pure-纯净+ity→纯净',
        'purlieu': 'pur-周围+lieu-地方→郊区',
        'purloin': 'pur-前+loin-腰部→偷窃',
        'purvey': 'pur-前+vey-看→供应',
        'pusillanimous': 'pusill-弱小+anim-精神+ous→怯懦的',
        'quaff': 'quaff-畅饮→痛饮',
        'quail': 'quail-鹌鹑→胆怯',
        'qualify': 'qual-性质+ify→限定',
        'quarry': 'quarry-采石场→猎物',
        'quash': 'quash-压碎→镇压',
        'quaver': 'quaver-颤抖→颤抖',
        'quixotic': 'Quixote-堂吉诃德+ic→空想的',
        'quota': 'quot-多少+a→配额',
        'rabble': 'rabble-乌合之众→暴民',
        'rabid': 'rab-狂怒+id→狂怒的',
        'racy': 'rac-种族+y→活泼的',
        'raffish': 'raff-乱糟糟+ish→低俗的',
        'raffle': 'raffle-抽彩→抽奖',
        'ragged': 'rag-破布+ged→破旧的',
        'rakish': 'rake-浪荡子+ish→潇洒的',
        'ramble': 'ram-漫游+ble→漫步',
        'ramshackle': 'ram-撞+shackle-镣铐→摇摇欲坠的',
        'random': 'random-随机→随机的',
        'rankle': 'rankle-化脓→激怒',
        'rant': 'rant-咆哮→咆哮',
        'rapport': 'ra-去+port-带→和谐关系',
        'rapprochement': 'rapproche-接近+ment→和解',
        'rapscallion': 'rap-抢+scallion-葱→恶棍',
        'rapt': 'rapt-被夺走的→全神贯注的',
        'rash': 'rash-皮疹→轻率的',
        'rarefy': 'rare-稀薄+fy→使稀薄',
        'raspy': 'rasp-锉刀+y→刺耳的',
        'ratiocination': 'rati-推理+ocination→推理',
        'ration': 'rat-计算+ion→配给',
        'rational': 'rat-计算+ional→理性的',
        'rave': 'rave-狂言→狂热赞扬',
        'ravel': 'ravel-纠缠→解开',
        'ravish': 'rav-抢夺+ish→使陶醉',
        'raze': 'raze-摧毁→夷为平地',
        'react': 're-反+act-行动→反应',
        'ream': 'ream-大量→大量钻孔',
        'reap': 'reap-收割→收获',
        'reassure': 're-再+assure-保证→使安心',
        'rebuff': 're-回+buff-打击→拒绝',
        'recessive': 're-回+cess-走+ive→隐性的',
        'recidivate': 're-重新+cid-落下+ate→累犯',
        'reciprocate': 're-反+cip-拿+roc-轮+ate→回报',
        'reckless': 'reck-注意+less→鲁莽的',
        'recoil': 're-回+coil-卷→退缩',
        'reconcile': 're-再+concile-安抚→和解',
        'recondite': 're-隐+cond-藏+ite→深奥的',
        'reconnoiter': 're-再+connoiter-了解→侦察',
        'reconstitute': 're-再+constitute-组成→重建',
        'reconvene': 're-再+convene-召集→再集会',
        'rectitude': 'rect-直+itude→正直',
        'redolent': 'red-回+ol-气味+ent→芳香的',
        'redundant': 're-反复+und-波浪+ant→多余的',
        'reel': 'reel-卷轴→蹒跚',
        'referee': 'refer-参考+ee→裁判',
        'refine': 're-再+fine-好→精炼',
        'reflect': 're-回+flect-弯曲→反射',
        'refulgent': 're-回+fulg-闪光+ent→灿烂的',
        'regenerate': 're-再+generate-产生→重生',
        'regimen': 'reg-统治+imen→养生法',
        'regress': 're-回+gress-走→倒退',
        'rehearsal': 're-再+hearse-耙+al→排练',
        'reign': 'reign-统治→统治',
        'rein': 'rein-缰绳→控制',
        'rejoice': 're-再+joice-快乐→欣喜',
        'release': 're-回+lease-放松→释放',
        'relentless': 'relent-怜悯+less→无情的',
        'relevant': 're-再+lev-举+ant→相关的',
        'religion': 're-再+lig-捆绑+ion→宗教',
        'relinquish': 're-再+linqu-离开+ish→放弃',
        'relish': 'relish-美味→享受',
        'reluctant': 're-反+luct-挣扎+ant→不情愿的',
        'remiss': 're-回+miss-放→疏忽的',
        'remodel': 're-再+model-模型→改造',
        'remonstrance': 're-反+monstr-展示+ance→抗议',
        'remunerate': 're-回+muner-礼物+ate→报酬',
        'rend': 'rend-撕裂→撕裂',
        'renounce': 're-回+nounce-宣布→放弃',
        'repartee': 're-回+partee-谈话→机智应答',
        'repatriate': 're-回+patri-祖国+ate→遣返',
        'repeal': 're-回+peal-驱赶→废除',
        'repel': 're-回+pel-推→击退',
        'repertoire': 're-再+pert-带+oire→剧目',
        'repose': 're-回+pose-放→休息',
        'reprehend': 're-回+prehend-抓住→谴责',
        'reproof': 're-反+proof-证明→责备',
        'reprove': 're-反+prove-证明→责骂',
        'requisite': 're-再+quis-寻求+ite→必需的',
        'reserved': 're-回+serv-保持+ed→保留的',
        'residue': 're-回+sid-坐+ue→残余',
        'resign': 're-回+sign-签署→辞职',
        'resilience': 're-回+sili-跳+ence→弹性',
        'resourceful': 're-再+source-源+ful→足智多谋的',
        'respire': 're-再+spire-呼吸→呼吸',
        'responsive': 're-回+spons-回应+ive→响应的',
        'restless': 'rest-休息+less→不安的',
        'resurgence': 're-再+surg-升起+ence→复兴',
        'resuscitate': 're-再+suscit-唤起+ate→复苏',
        'retainer': 're-回+tain-保持+er→聘用定金',
        'retinue': 're-回+tin-保持+ue→随从',
        'retort': 're-回+tort-扭→反驳',
        'retouch': 're-再+touch-触碰→润色',
        'revelry': 'revel-狂欢+ry→狂欢',
        'revenge': 're-回+venge-报仇→复仇',
        'revise': 're-再+vis-看+e→修订',
        'revive': 're-再+viv-活+e→复苏',
        'ribald': 'ribald-下流→粗俗的',
        'rickety': 'ricket-佝偻+y→摇摇晃晃的',
        'rider': 'rid-骑+er→附加条款',
        'ridicule': 'ridic-笑+ule→嘲笑',
        'rife': 'rife-丰富的→流行的',
        'rile': 'rile-搅浑→激怒',
        'ripen': 'ripe-成熟+n→使成熟',
        'rite': 'rite-仪式→典礼',
        'rive': 'rive-撕裂→劈开',
        'riveting': 'rivet-铆钉+ing→引人入胜的',
        'rivulet': 'riv-河+ulet→小溪',
        'roil': 'roil-搅浑→激怒',
        'roisterer': 'roister-喧闹+er→喧闹者',
        'rookie': 'rookie-新兵→新手',
        'rouse': 'rouse-唤醒→唤醒',
        'royalty': 'royal-王室+ty→版税',
        'rubicund': 'rubi-红+cund→红润的',
        'ruffle': 'ruffle-弄皱→使混乱',
        'rumple': 'rumple-弄皱→使凌乱',
        'run': 'run-跑→竞选',
        'runic': 'rune-神秘文字+ic→神秘的',
        'ruse': 'ruse-诡计→计谋',
        'rustle': 'rustle-沙沙声→窸窣',
        'saccharine': 'sacchar-糖+ine→甜腻的',
        'saddle': 'saddle-马鞍→给负担',
        'safeguard': 'safe-安全+guard-守卫→保护',
        'sage': 'sage-鼠尾草→智者',
        'salubrious': 'salubr-健康+ious→健康的',
        'salutation': 'salut-健康+ation→问候',
        'salve': 'salve-药膏→安慰',
        'sanctify': 'sanct-神圣+ify→使神圣',
        'sanitary': 'sanit-健康+ary→卫生的',
        'sapient': 'sapi-智慧+ent→有智慧的',
        'sartorial': 'sartor-裁缝+ial→裁缝的',
        'sate': 'sate-满足→使满足',
        'satirize': 'satire-讽刺+ize→讽刺',
        'saturnine': 'Saturn-土星+ine→阴郁的',
    }

def build_example(item):
    """Build a 15-20 word example sentence with <b>bold</b> formatting."""
    name = item['name']
    
    # Collect all non-empty examples
    examples = []
    for i in range(1, 5):
        eg = item.get(f'eg{i}', '')
        if eg:
            eng = re.sub(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]+.*$', '', eg).strip()
            eng = eng.strip('。，,; ')
            if eng:
                examples.append(eng)
    
    if not examples:
        return f"The concept of <b>{name}</b> is important in GRE reading comprehension."
    
    # Find the best example containing the word (possibly inflected)
    def find_word_span(text, word):
        """Find a word and possible inflected forms (e.g. 'rages' for 'rage', 'repudiated' for 'repudiate')."""
        # Direct match first
        m = re.search(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE)
        if m:
            return m.start(), m.end()
        # Try with common suffixes
        for suffix in ['s', 'es', 'ed', 'ing', 'd', 'er', 'ers', 'ly']:
            inflected = word + suffix
            m = re.search(r'\b' + re.escape(inflected) + r'\b', text, re.IGNORECASE)
            if m:
                return m.start(), m.end()
        return None
    
    def contains_word(text, word):
        return find_word_span(text, word) is not None
    
    best_eg = examples[0]
    for eg in examples:
        if contains_word(eg, name):
            best_eg = eg
            break
    
    # Now find the word (possibly inflected) in the sentence
    span = find_word_span(best_eg, name)
    
    if not span:
        best_eg = f"The term <b>{name}</b> is used to describe this phenomenon."
    else:
        start, end = span
        actual_word = best_eg[start:end]
        
        # Get up to 2 following words for context
        rest_after = best_eg[end:].strip()
        after_words = rest_after.split()
        bold_extra = []
        for w in after_words:
            if len(bold_extra) >= 2:
                break
            w_clean = w.strip('.,;:')
            if w_clean:
                bold_extra.append(w_clean)
        
        bold_part = actual_word
        if bold_extra:
            bold_part += ' ' + ' '.join(bold_extra)
        
        before = best_eg[:start].rstrip()
        after = ' '.join(after_words[len(bold_extra):])
        
        best_eg = f"{before} <b>{bold_part}</b> {after}".strip()
        best_eg = re.sub(r'\s+', ' ', best_eg)
    
    # Ensure it ends with period and is reasonable length
    best_eg = best_eg.rstrip('.')
    words = best_eg.split()
    if len(words) > 20:
        best_eg = ' '.join(words[:20])
    if not best_eg.endswith('.'):
        best_eg += '.'
    
    # Fix any weird spacing near <b> tags
    best_eg = best_eg.replace('> <b>', '> <b>').replace('<b> ', '<b>')
    
    return best_eg

def build_changkao(item, syn_words, ant_words):
    """Build changkao field with specific collocations, synonym/antonym relations, and GRE reading context."""
    name = item['name']
    pos = item.get('pos1', '')
    meaning1 = item.get('meaning1', '')
    meaning_cn = extract_meaning(pos, meaning1)
    
    cn_part = meaning_cn.replace(pos, '').strip()
    if cn_part.startswith('、'):
        cn_part = cn_part[1:]
    
    syn_str = '、'.join(syn_words[:4]) if syn_words else "（待补充）"
    ant_str = '、'.join(ant_words[:4]) if ant_words else "（待补充）"
    
    # Get collocation from example (handle inflected forms)
    eg = item.get('eg1', '')
    eg_english = re.sub(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]+.*$', '', eg).strip() if eg else ""
    
    def find_any_form_pos(text, word):
        m = re.search(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE)
        if m:
            return m.start()
        for suffix in ['s', 'es', 'ed', 'ing', 'd', 'er', 'ers', 'ly']:
            m = re.search(r'\b' + re.escape(word + suffix) + r'\b', text, re.IGNORECASE)
            if m:
                return m.start()
        return -1
    
    collocation = ""
    if eg_english:
        pos_in_eg = find_any_form_pos(eg_english, name)
        if pos_in_eg >= 0:
            words = eg_english.split()
            for i, w in enumerate(words):
                w_clean = w.strip('.,;:')
                if w_clean.lower().startswith(name.lower()):
                    start = max(0, i-2)
                    end = min(len(words), i+3)
                    collocation = ' '.join(words[start:end])
                    break
    
    colloc_text = f"，常与「{collocation}」搭配" if collocation else ""
    
    return f"· 常考：{name} 指{cn_part}，与{syn_str}近义，与{ant_str}反义{colloc_text}，GRE阅读中常用于描述相关概念，需注意辨析近义词的细微差别"

def build_exam_tips(syn_words, ant_words):
    """Build exam_tips with 💡同义 and 反义."""
    syn_str = ', '.join(syn_words[:4]) if syn_words else "(待补充)"
    ant_str = ', '.join(ant_words[:4]) if ant_words else "(待补充)"
    return f'💡同义：{syn_str} | 反义：{ant_str}'

def main():
    with open('/home/Lu/gre_batch_7_raw.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    roots = get_word_roots()
    output_lines = []
    errors = []
    
    for idx, item in enumerate(data):
        name = item['name']
        pos1 = item.get('pos1', '')
        meaning1 = item.get('meaning1', '')
        
        try:
            # --- meaning_cn ---
            meaning_cn = extract_meaning(pos1, meaning1)
            if not meaning_cn or meaning_cn.strip() == pos1.strip():
                pos2 = item.get('pos2', '')
                meaning2 = item.get('meaning2', '')
                if pos2 and meaning2:
                    meaning_cn = extract_meaning(pos2, meaning2)
            if not meaning_cn or meaning_cn.strip() == pos1.strip():
                meaning_cn = f"{pos1}（待补充释义）" if pos1 else "（待补充）"
            
            # --- synonyms and antonyms ---
            syn1 = parse_synonyms(item.get('syn1', ''))
            syn2 = parse_synonyms(item.get('syn2', ''))
            all_syn = list(dict.fromkeys(syn1 + syn2))
            
            ant1 = parse_antonyms(item.get('ant1', ''))
            ant2 = parse_antonyms(item.get('ant2', ''))
            all_ant = list(dict.fromkeys(ant1 + ant2))
            
            # --- memo ---
            # Clean name for lookup (remove any rogue sound tag embedded in name)
            clean_name = re.sub(r'\[sound:.*?\]', '', name).strip()
            root = roots.get(clean_name)
            if root:
                memo = f'⭐词根：{root}'
            else:
                memo = f'⭐词根：{clean_name}（待补充详细拆解）'
            
            # --- example ---
            example = build_example(item)
            
            # --- changkao ---
            changkao = build_changkao(item, all_syn, all_ant)
            
            # --- exam_tips ---
            exam_tips = build_exam_tips(all_syn, all_ant)
            
            output = {
                'name': name,
                'meaning_cn': meaning_cn,
                'memo': memo,
                'example': example,
                'changkao': changkao,
                'exam_tips': exam_tips
            }
            
            output_lines.append(json.dumps(output, ensure_ascii=False))
        except Exception as e:
            errors.append(f"[{idx}] {name}: {e}")
            output_lines.append(json.dumps({'name': name, 'meaning_cn': '(error)', 'memo': '(error)', 'example': '(error)', 'changkao': '(error)', 'exam_tips': '(error)'}, ensure_ascii=False))
    
    with open('/home/Lu/gre_batch_7_done.json', 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines) + '\n')
    
    print(f"✅ Processed {len(output_lines)} words from {data[0]['name']} to {data[-1]['name']}")
    if errors:
        print(f"⚠️  {len(errors)} errors:")
        for e in errors:
            print(f"   {e}")
    print(f"Output written to /home/Lu/gre_batch_7_done.json")

if __name__ == '__main__':
    main()
