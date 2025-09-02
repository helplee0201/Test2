WEB_DATA = [
    "202304 7978702030 (주)온길 8388102760 (주)유빈씨앤아이 외상매입금 3 2 6,471,391",
    "202304 7978702030 (주)온길 8388102760 (주)유빈씨앤아이 외상매출금 4 3 25,123,162",
    "202304 3208102629 (주)신안컴퍼니대구본부 1498802150 (유한)엠케이피드 부가세대급금 3 1 4,545,455",
    "202304 3578100676 주식회사 소프런(본점) 5108701021 (주)제이에이치월드 판매수수료 3 1 7,603,200",
    "202304 3578100676 주식회사 소프런(본점) 5108701021 (주)제이에이치월드 미지급금 3 1 37,264,500",
    "202304 3578100676 주식회사 소프런(본점) 5108701021 (주)제이에이치월드 외상매입금 4 1 8,363,520",
    "202304 3578100676 주식회사 소프런(본점) 5108701021 (주)제이에이치월드 외상매입금 3 1 11,985,600",
    "202304 3578100676 주식회사 소프런 5108701021 (주)제이에이치월드 판매수수료 3 1 7,603,200",
    "202304 1318607714 (주)현대렌탈서비스 4078133069 (주)큰마당/ 김기석 부가세예수금 4 1 5,000,000",
    "202304 1318607714 (주)현대렌탈서비스 4078133069 (주)큰마당/ 김기석 잡이익 4 1 50,000,000",
    "202304 1308605902 (주)JS개발 5108701021 (주)제이에이치월드 임대료수입 4 1 3,293,333",
    "202304 1308605902 (주)JS개발 5108701021 (주)제이에이치월드 임대보증금 3 1 52,000,000",
    "202304 1308605902 (주)JS개발 5108701021 (주)제이에이치월드 선수금 3 1 158,000,000",
    "202304 1308605902 (주)JS개발 5108701021 (주)제이에이치월드 부가세예수금 4 2 50,329,333",
    "202304 3578100676 주식회사 소프런 5108701021 (주)제이에이치월드 미지급금 3 1 37,264,500",
    "202304 3578100676 주식회사 소프런 5108701021 (주)제이에이치월드 외상매입금 4 1 8,363,520",
    "202304 3578100676 주식회사 소프런 5108701021 (주)제이에이치월드 외상매입금 3 1 11,985,600",
    "202304 1308605902 (주)JS개발 5108701021 (주)제이에이치월드 임대료수입 4 1 3,293,333",
    "202304 1308605902 (주)JS개발 5108701021 (주)제이에이치월드 임대보증금 3 1 52,000,000",
    "202304 1308605902 (주)JS개발 5108701021 (주)제이에이치월드 선수금 3 1 158,000,000",
    "202304 1308605902 (주)JS개발 5108701021 (주)제이에이치월드 부가세예수금 4 2 50,329,333",
    "202304 1308605902 (주)JS개발 5108701021 (주)제이에이치월드 건물 4 1 500,000,000",
    "202309 2998801607 주식회사 렌탈파인통합 8388102760 (주)유빈씨앤아이 렌탈료수입 4 1 3,156,000",
    "202309 2998801607 주식회사 렌탈파인통합 8388102760 (주)유빈씨앤아이 보통예금 3 1 3,471,600",
    "202309 1078681268 (주)한담 22년까지 확정 기장분 7058100744 주식회사선진중기계문희동, 이인애 미지급금 4 1 28,710,000",
    "202309 1078836826 (주)디엠케이코리아 5108701021 (주)제이에이치월드 미수금 4 2 4,961,479",
    "202309 1078836826 (주)디엠케이코리아 5108701021 (주)제이에이치월드 선급금 3 1 30,000,000",
    "202309 1078836826 (주)디엠케이코리아 5108701021 (주)제이에이치월드 임대료수입 4 2 4,531,188",
    "202309 2998801607 주식회사 이오케이(통합) 3128190802 (주)동우에프엔씨 보통예금 3 1 3,331,900"
]

PARSED_DATA = []
for line in WEB_DATA:
    parts = [part for part in line.split() if part]
    if len(parts) < 8:  # Minimum parts: dm_data, no_biz, nm_krcom, no_bisocial, nm_trade, nm_acctit, ty_gubn, ct_bungae
        continue
    idx = 0
    dm_data = parts[idx]
    idx += 1
    no_biz = parts[idx]
    if not (no_biz.isdigit() and len(no_biz) == 10):
        continue
    idx += 1
    nm_krcom_parts = []
    while idx < len(parts) and not (parts[idx].isdigit() and len(parts[idx]) == 10):
        nm_krcom_parts.append(parts[idx])
        idx += 1
    if idx >= len(parts):
        continue
    no_bisocial = parts[idx]
    if not (no_bisocial.isdigit() and len(no_bisocial) == 10):
        continue
    idx += 1
    nm_trade_parts = []
    # Collect nm_trade until a single-word nm_acctit (non-numeric, non-digit)
    while idx < len(parts) and not parts[idx].isdigit():
        nm_trade_parts.append(parts[idx])
        idx += 1
    if idx >= len(parts):
        continue
    nm_acctit = parts[idx - 1]  # nm_acctit is the last non-numeric part before digits
    nm_trade = ' '.join(nm_trade_parts[:-1]) if nm_trade_parts else ''
    if idx >= len(parts):
        continue
    ty_gubn = parts[idx]
    if not ty_gubn.isdigit():
        continue
    idx += 1
    ct_bungae = parts[idx] if idx < len(parts) else '0'
    if not ct_bungae.isdigit():
        continue
    idx += 1
    mn_bungae = parts[idx] if idx < len(parts) else '0'
    if not all(c.isdigit() or c == ',' for c in mn_bungae):
        continue
    nm_krcom = ' '.join(nm_krcom_parts)
    PARSED_DATA.append({
        "dm_data": dm_data,
        "no_biz": no_biz,
        "nm_krcom": nm_krcom,
        "no_bisocial": no_bisocial,
        "nm_trade": nm_trade,
        "nm_acctit": nm_acctit,
        "ty_gubn": ty_gubn,
        "ct_bungae": ct_bungae,
        "mn_bungae": mn_bungae
    })