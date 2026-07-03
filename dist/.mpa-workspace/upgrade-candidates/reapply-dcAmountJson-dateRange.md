---
type: A
title: dcAmountJson 다중 구간 정책의 calendar 재생성 시 구간 정보 누락
session: 2026-06-23
---

## 오판 내용

`reapplyOverlappingPolicies` 초기 구현에서 `saveDcEventCalendar(dcEventId)` 단순 호출.
dcAmountJson 정책은 각 dcEvent가 구간별 dateFrom/dateTo로 생성되었으나, 재생성 시 파라미터 없이 호출 → 전체 날짜 범위로 덮어쓰기 발생.

## 패턴

"기존 dcEvent를 재사용하는 코드 경로"에서는 원본 삽입 경로(`insertDcEventsAndCalendar`)가 사용한 오버로드 시그니처도 함께 확인해야 한다.
특히 오버로드가 `null → 정책 기본값 사용` 구조일 때 누락 여부를 의식적으로 점검한다.

## 수정

`rebuildDcEventCalendar` 헬퍼 추가: dcAmountJson 존재 시 `buildDcEventGroupList`로 구간 재계산 후 index 대응으로 `saveDcEventCalendar(dcEventId, dateFrom, dateTo)` 호출.
