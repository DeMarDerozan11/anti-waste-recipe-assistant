"""Liste d'aliments proposee a l'utilisateur, par categorie, avec leur nom dans chaque langue.

Le nom anglais sert a la recherche : il suit le vocabulaire du jeu de donnees.
"""
from dataclasses import dataclass

from src.matching import tokens

LANGS = ("en", "fr", "es", "ja")

# Chaque ligne : en | fr | es | ja
_RAW = {
    "meat": ("Viandes et volailles|Meat and poultry|Carnes y aves|肉類", """
        chicken|poulet|pollo|鶏肉
        chicken breast|blanc de poulet|pechuga de pollo|鶏むね肉
        chicken thigh|cuisse de poulet|muslo de pollo|鶏もも肉
        ground beef|bœuf haché|carne picada de res|牛ひき肉
        beef steak|steak de bœuf|filete de res|牛ステーキ肉
        pork chop|côte de porc|chuleta de cerdo|豚ロース肉
        ground pork|porc haché|carne picada de cerdo|豚ひき肉
        bacon|bacon|beicon|ベーコン
        ham|jambon|jamón|ハム
        sausage|saucisse|salchicha|ソーセージ
        chorizo|chorizo|chorizo|チョリソー
        turkey|dinde|pavo|七面鳥
        lamb|agneau|cordero|ラム肉
        duck|canard|pato|鴨肉"""),
    "seafood": ("Poissons et fruits de mer|Fish and seafood|Pescados y mariscos|魚介類", """
        salmon|saumon|salmón|サーモン
        tuna|thon|atún|ツナ
        cod|cabillaud|bacalao|タラ
        shrimp|crevette|gamba|エビ
        sardine|sardine|sardina|イワシ
        crab|crabe|cangrejo|カニ
        mussel|moule|mejillón|ムール貝
        squid|calamar|calamar|イカ
        smoked salmon|saumon fumé|salmón ahumado|スモークサーモン"""),
    "dairy": ("Œufs et produits laitiers|Eggs and dairy|Huevos y lácteos|卵・乳製品", """
        egg|œuf|huevo|卵
        milk|lait|leche|牛乳
        butter|beurre|mantequilla|バター
        heavy cream|crème liquide|nata para cocinar|生クリーム
        sour cream|crème aigre|crema agria|サワークリーム
        yogurt|yaourt|yogur|ヨーグルト
        cheddar cheese|cheddar|queso cheddar|チェダーチーズ
        mozzarella|mozzarella|mozzarella|モッツァレラ
        parmesan|parmesan|parmesano|パルメザン
        feta|feta|feta|フェタ
        cream cheese|fromage à tartiner|queso crema|クリームチーズ
        goat cheese|fromage de chèvre|queso de cabra|ヤギのチーズ"""),
    "vegetables": ("Légumes|Vegetables|Verduras|野菜", """
        onion|oignon|cebolla|玉ねぎ
        garlic|ail|ajo|にんにく
        tomato|tomate|tomate|トマト
        potato|pomme de terre|patata|じゃがいも
        sweet potato|patate douce|batata|さつまいも
        carrot|carotte|zanahoria|にんじん
        bell pepper|poivron|pimiento|パプリカ
        zucchini|courgette|calabacín|ズッキーニ
        eggplant|aubergine|berenjena|なす
        broccoli|brocoli|brócoli|ブロッコリー
        cauliflower|chou-fleur|coliflor|カリフラワー
        spinach|épinards|espinacas|ほうれん草
        lettuce|salade verte|lechuga|レタス
        cucumber|concombre|pepino|きゅうり
        mushroom|champignon|champiñón|きのこ
        celery|céleri|apio|セロリ
        leek|poireau|puerro|リーキ
        cabbage|chou|col|キャベツ
        green bean|haricot vert|judía verde|さやいんげん
        pea|petit pois|guisante|グリーンピース
        corn|maïs|maíz|とうもろこし
        pumpkin|citrouille|calabaza|かぼちゃ
        asparagus|asperge|espárrago|アスパラガス
        beet|betterave|remolacha|ビーツ
        radish|radis|rábano|ラディッシュ
        green onion|oignon vert|cebolleta|青ねぎ
        ginger|gingembre|jengibre|しょうが"""),
    "fruits": ("Fruits|Fruit|Frutas|果物", """
        apple|pomme|manzana|りんご
        banana|banane|plátano|バナナ
        lemon|citron|limón|レモン
        lime|citron vert|lima|ライム
        orange|orange|naranja|オレンジ
        strawberry|fraise|fresa|いちご
        blueberry|myrtille|arándano|ブルーベリー
        raspberry|framboise|frambuesa|ラズベリー
        pear|poire|pera|洋なし
        peach|pêche|melocotón|桃
        grape|raisin|uva|ぶどう
        pineapple|ananas|piña|パイナップル
        mango|mangue|mango|マンゴー
        avocado|avocat|aguacate|アボカド
        coconut|noix de coco|coco|ココナッツ
        cherry|cerise|cereza|さくらんぼ
        kiwi|kiwi|kiwi|キウイ
        watermelon|pastèque|sandía|すいか"""),
    "grains": ("Féculents et céréales|Grains and starches|Cereales y féculas|穀物・主食", """
        rice|riz|arroz|米
        pasta|pâtes|pasta|パスタ
        spaghetti|spaghetti|espaguetis|スパゲッティ
        noodle|nouilles|fideos|麺
        bread|pain|pan|パン
        couscous|couscous|cuscús|クスクス
        quinoa|quinoa|quinoa|キヌア
        oat|flocons d'avoine|avena|オートミール
        bulgur|boulgour|bulgur|ブルグル
        tortilla|tortilla|tortilla|トルティーヤ
        breadcrumb|chapelure|pan rallado|パン粉
        cornmeal|semoule de maïs|harina de maíz|コーンミール"""),
    "legumes": ("Légumineuses et protéines végétales|Legumes and plant proteins|Legumbres y proteínas vegetales|豆類・植物性たんぱく", """
        lentil|lentilles|lentejas|レンズ豆
        chickpea|pois chiches|garbanzos|ひよこ豆
        black bean|haricot noir|frijoles negros|ブラックビーンズ
        kidney bean|haricot rouge|alubias rojas|赤いんげん豆
        white bean|haricot blanc|alubias blancas|白いんげん豆
        tofu|tofu|tofu|豆腐
        peanut|cacahuète|cacahuete|ピーナッツ"""),
    "grocery": ("Épicerie|Pantry|Despensa|食料品", """
        canned tomato|tomates en conserve|tomate en conserva|トマト缶
        tomato sauce|sauce tomate|salsa de tomate|トマトソース
        tomato paste|concentré de tomate|concentrado de tomate|トマトペースト
        soy sauce|sauce soja|salsa de soja|醤油
        honey|miel|miel|はちみつ
        vinegar|vinaigre|vinagre|酢
        mustard|moutarde|mostaza|マスタード
        mayonnaise|mayonnaise|mayonesa|マヨネーズ
        ketchup|ketchup|kétchup|ケチャップ
        peanut butter|beurre de cacahuète|mantequilla de cacahuete|ピーナッツバター
        jam|confiture|mermelada|ジャム
        chocolate|chocolat|chocolate|チョコレート
        cocoa|cacao|cacao|ココア
        coconut milk|lait de coco|leche de coco|ココナッツミルク
        chicken broth|bouillon de poulet|caldo de pollo|チキンブイヨン
        vegetable broth|bouillon de légumes|caldo de verduras|野菜ブイヨン
        baking powder|levure chimique|levadura química|ベーキングパウダー
        vanilla|vanille|vainilla|バニラ
        almond|amande|almendra|アーモンド
        walnut|noix|nuez|くるみ
        olive|olive|aceituna|オリーブ
        caper|câpres|alcaparras|ケッパー
        maple syrup|sirop d'érable|sirope de arce|メープルシロップ
        sesame oil|huile de sésame|aceite de sésamo|ごま油
        miso|miso|miso|味噌"""),
    "spices": ("Herbes et épices|Herbs and spices|Hierbas y especias|ハーブ・スパイス", """
        basil|basilic|albahaca|バジル
        parsley|persil|perejil|パセリ
        cilantro|coriandre|cilantro|パクチー
        thyme|thym|tomillo|タイム
        rosemary|romarin|romero|ローズマリー
        oregano|origan|orégano|オレガノ
        mint|menthe|menta|ミント
        dill|aneth|eneldo|ディル
        chives|ciboulette|cebollino|チャイブ
        paprika|paprika|pimentón|パプリカパウダー
        cumin|cumin|comino|クミン
        curry powder|curry en poudre|curry en polvo|カレー粉
        cinnamon|cannelle|canela|シナモン
        chili pepper|piment|guindilla|唐辛子
        nutmeg|muscade|nuez moscada|ナツメグ
        turmeric|curcuma|cúrcuma|ターメリック
        bay leaf|feuille de laurier|hoja de laurel|ローリエ
        garlic powder|ail en poudre|ajo en polvo|ガーリックパウダー"""),
}


@dataclass(frozen=True)
class Item:
    en: str
    labels: dict


@dataclass(frozen=True)
class Category:
    key: str
    labels: dict
    items: tuple


def _parse() -> list[Category]:
    categories = []
    for key, (names, rows) in _RAW.items():
        # Les libelles de categorie sont ecrits fr|en|es|ja, ceux des aliments en|fr|es|ja.
        fr, en, es, ja = names.split("|")
        items = []
        for line in rows.strip().splitlines():
            parts = [p.strip() for p in line.split("|")]
            items.append(Item(parts[0], dict(zip(LANGS, parts))))
        categories.append(Category(key, {"fr": fr, "en": en, "es": es, "ja": ja}, tuple(items)))
    return categories


CATEGORIES = _parse()
_BY_NAME = {item.en: item for category in CATEGORIES for item in category.items}
_BY_TOKENS = {tokens(item.en): item for item in _BY_NAME.values()}


def item_label(name: str, language: str) -> str:
    item = _BY_NAME.get(name)
    return item.labels[language] if item else name


def local_label(term: str, language: str) -> str | None:
    """Nom d'un ingredient dans la langue voulue, s'il est dans la liste (sinon None)."""
    item = _BY_TOKENS.get(tokens(term))
    return item.labels[language] if item else None


def match_item(name: str) -> str | None:
    """Aliment de la liste qui correspond a un nom libre : 'red onions' -> 'onion'."""
    wanted = tokens(name)
    if not wanted:
        return None
    exact = _BY_TOKENS.get(wanted)
    if exact:
        return exact.en
    inside = [item for key, item in _BY_TOKENS.items() if key <= wanted]
    return max(inside, key=lambda item: len(tokens(item.en))).en if inside else None
