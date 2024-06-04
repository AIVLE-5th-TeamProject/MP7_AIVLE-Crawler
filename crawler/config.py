config = {
    "path": {
        "chrome_driver"   : f"./chromedriver.exe",
        "output_directory": f"./documents",        
    },
    "url": {
        "aivle_url" : r"https://aivle.kt.co.kr/home/brd/faq/main?mcd=MC00000056",    
        "google_search" : r"https://www.google.com/search?q=%EC%97%90%EC%9D%B4%EB%B8%94%EC%8A%A4%EC%BF%A8+%ED%9B%84%EA%B8%B0+AIVLE+OR+OR+OR+%EC%97%90%EC%9D%B4%EC%81%A0+OR+OR+OR+%EC%97%90%EC%9D%B4%EB%B8%94%EA%B8%B0%EC%9E%90%EB%8B%A8+OR+OR+OR+%EC%BD%94%EB%94%A9%EB%A7%88%EC%8A%A4%ED%84%B0%EC%8A%A4+OR+OR+OR+%EC%97%90%EC%9D%B4%EB%B8%94%EC%8A%A4%EC%BF%A8%ED%9B%84%EA%B8%B0+OR+OR+OR+%EB%AF%B8%EB%8B%88%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8+OR+OR+OR+%EB%B9%85%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8&lr=&sca_esv=1a54e3a5b2edf263&sca_upv=1&sxsrf=ADLYWIL6CNapBlzvWvvQ8uULp9ESCFcSeQ:1717476872154&tbas=0&source=lnt&sa=X&ved=2ahUKEwj_jf_2k8GGAxV7slYBHfoiAsIQpwV6BAgCEAs&cshid=1717476894283904&biw=1536&bih=730&dpr=1.25#ip=1",
    },
    "selector" : {
        "faq_list"   : "#faqList > li",
        "category"   : "div.question > p.cate > span",
        "question"   : "div.question > p.subject",
        "answer"     : "div.answer",
        "more_button": "#btn > a",
        "search_result": "div.kb0PBd.cvP2Ce.A9Y9g.jGGQ5e > div > div > span > a"
    }
}