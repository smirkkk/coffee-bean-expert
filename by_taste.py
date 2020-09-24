import pandas as pd
import numpy as np
import csv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


bean_list = [
    '가상의 원두',
    '벽난로 블렌드',
    '도미닉 블렌딩',
    '과테말라 JDL Selection',
    '모닥불 블렌드',
    '장작 블렌드',
    '양초 블렌드',
    '땡얼 과테말라 오카나',
    '땡얼 몬테데오로 내추럴',
    '땡얼 엘살바도르 쿠스카틀레코',
    '언더프레셔 골든 에라 블렌드',
    '언더프레셔 브루클린 컴포트 블렌드',
    '땡얼 과테말라 와이칸',
    '땡얼 데일리 스윗 플러스',
    '이월 엘살파도르 SHG',
    '정월 블렌드',
    '만월 블렌드',
    '이월 블렌드',
    '에스페란토 노사세뇨라 아파레시다',
    '에스페란토 엘트리파체',
    '에스페란토 AA TOP',
    '에스페란토 부에노스 아이레스'
]

class2_list = [
    '갈색 설탕', '감귤류', '거친',
    '견과', '그린/야채', '기타과일',
    '꽃', '달콤한 향료', '담배',
    '말린 과일', '바닐라', '바닐라 첨가향',
    '베리류', '시큼한', '신선한',
    '알코올/발효된', '올리브유', '전반적으로 달콤한',
    '종이/퀴퀴한', '코코아', '탄',
    '톡 쏘는', '파이프 담배', '홍차',
    '화학약품', '황색 향신료', '후추'
]


def set_virtual_bean():
    print('숫자로 입력, 쉼표로 구분')
    print("""
    1. 갈색설탕            2. 감귤류          3. 거친
    4. 견과                5. 그린/야채         6. 기타과일
    7. 꽃                  8. 달콤한향료        9. 담배
    10. 말린 과일            11. 바닐라          12. 바닐라첨가향
    13. 베리류             14. 시큼한            15. 신선한
    16. 알코올/발효된       17. 올리브유          18. 전반적으로달콤한
    19. 종이/퀴퀴한         20. 코코아          21. 탄
    22. 톡쏘는            23. 파이프담배      24. 홍차
    25. 화학약품            26. 황색향신료      27. 후추 
    """)

    selected_id = input('입력 : ').split(',')
    selected_list = []

    for x in selected_id:
        selected_list.append(class2_list[int(x) - 1])

    print(selected_list)
    selected_list = ('|').join(selected_list)

    bean_csv = pd.read_csv('./csv_storage/bean_raw_data.csv', encoding="CP949")

    bean_csv['bean_name'][0] = '가상의 원두'
    bean_csv['tasting_note'][0] = selected_list
    bean_csv.to_csv('./csv_storage/bean_raw_data.csv', encoding="CP949")


def get_matrix():
    beans = pd.read_csv('./csv_storage/bean_raw_data.csv', encoding="CP949")
    # print(beans.columns)

    beans_df = beans[['bean_name', 'tasting_note']]

    beans_df['tasting_note'] = beans_df['tasting_note'].str.split('|')
    # print(beans_df['tasting_note'])
    beans_df['tasting_note_literal'] = beans_df['tasting_note'].apply(
        lambda x: (' ').join(x) if type(x) == list else '')

    # print(beans_df['tasting_note_literal'])

    count_vect = CountVectorizer(min_df=0, ngram_range=(1, 1))
    beans_mat = count_vect.fit_transform(beans_df['tasting_note_literal'])

    box = []
    for i in beans_df['tasting_note']:
        if type(i) == list:
            for v in i:
                box.append(v)

    new_tasting_note = pd.Series(box)
    # 판다스의 .unique()메소드를 사용하여 중복되는 장르값을 제거한다.
    new_tasting_note = new_tasting_note.unique()
    # print(new_tasting_note)

    tasting_note_num = dict(zip(range(len(new_tasting_note)), list(new_tasting_note)))
    # >> {0: 'Action', 1: 'Adventure'..}

    # key와 values를 바꿔주는 작업 진행
    new_tasting_note_id = {v: k for k, v in tasting_note_num.items()}
    # print(new_tasting_note_id)

    box = []
    for i in beans_df['tasting_note']:
        mini_box = []
        if type(i) == list:
            for v in i:
                if v in new_tasting_note_id.keys():
                    mini_box.append(new_tasting_note_id[v])
            box.append(mini_box)

    score = np.zeros((beans_df['bean_name'].nunique(), beans_df['tasting_note_literal'].nunique()))

    for i, v in enumerate(box):
        for w in v:
            score[i, w] = 1.0

    return beans_df, score


def get_result(beans_df, score):
    cosine_similar = cosine_similarity(score, score)

    # 자기 자신에 대한 유사도는 가끔 0.99999997 이 있기 때문에 사전 처리
    for i in range(beans_df['bean_name'].nunique()):
        cosine_similar[i, i] = 1.0

    cosine_similar_data = pd.DataFrame(data=cosine_similar, index=bean_list)
    # print(cosine_similar_data)

    # print('가장 인상 깊었던 원두는?\n')
    # for i, x in enumerate(bean_list[1:], 1):
    #     print('{}. {}'.format(str(i), x))
    #
    # bean_id = int(input("""입력 : """))

    result = cosine_similar_data[0].sort_values(ascending=False)

    print('\n\n\n\n\n추천 순위\n\n')
    print(result)

    return result


if __name__ == '__main__':
    set_virtual_bean()
    beans_df, score = get_matrix()
    get_result(beans_df, score)
