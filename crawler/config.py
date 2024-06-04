config = {
    "path": {
        "chrome_driver"   : f"./chromedriver.exe",
        "output_directory": "./documents",        
    },
    "url": {
        "aivle_url" : "https://aivle.kt.co.kr/home/brd/faq/main?mcd=MC00000056",    
    },
    "selector" : {
        "faq_list"   : "#faqList > li",
        "category"   : "div.question > p.cate > span",
        "question"   : "div.question > p.subject",
        "answer"     : "div.answer",
        "more_button": "#btn > a"
    }
}