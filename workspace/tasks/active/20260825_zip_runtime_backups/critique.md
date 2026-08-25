# 계획 비평: 성공 배포 Runtime 백업의 ZIP 보관

## 파급효과 높은 미해소 결정

- **압축 실패를 배포 성공으로 처리하는 상태 계약이 불완전하다.** 계획은 새 Runtime을 유지하고 디렉터리 backup을 보존하며 `archive 미완료`를 기록한다고만 한다. 이 상태의 marker·receipt·backup metadata가 각각 무엇을 의미하는지, 이후 배포/rollback/retention이 이를 성공 백업·실패 백업·재시도 대상으로 어떻게 분류하는지가 없다. 이 경계가 모호하면 다음 deploy가 fallback 디렉터리를 관리형 백업으로 오인하거나, 반대로 rollback 가능한 최신 상태를 찾지 못할 수 있다.

- **archive 재시도·정리의 책임자가 없다.** archive 미완료 디렉터리는 자동 retention 대상에서 제외하는데, 재시도 시점과 실행 주체, 영구적으로 남을 때의 운영 경고·용량 상한이 정의되지 않았다. 한 번의 저장장치 문제로 backup 디렉터리가 계속 누적되어, 이번 변경이 해결하려는 파일·공간 문제를 장기적으로 다시 만들 수 있다.

- **ZIP의 원자적 publish 방법이 정해지지 않았다.** 최종 ZIP 경로에 직접 쓰면 프로세스 중단·디스크 full·동시 관찰 시 불완전 ZIP이 남을 수 있다. 임시 파일 작성, fsync/close, 검증, 원자 rename, 실패 산출물 격리·삭제의 순서와 파일명 규칙이 없어서 “무결성 확인 후 원본 삭제”가 실제로 crash-safe하다는 보장이 없다.

- **안전한 해제의 보안 계약이 부족하다.** “안전한 임시 해제 helper”만으로는 zip-slip(`../`), 절대경로, symlink/hardlink, 중복·대소문자 충돌, 과도한 압축비(zip bomb), 예상 밖 파일을 어떻게 차단할지 알 수 없다. rollback은 대상 Runtime을 교체하는 고권한 경로이므로, backup이 로컬이라고 가정해도 손상·변조 ZIP이 대상 외 경로 쓰기 또는 복구 데이터 오염으로 이어질 수 있다.

- **무결성 검증의 기준이 명확하지 않다.** asset map·marker 검증이라고 하나, ZIP 내부 파일 목록/모드/체크섬을 무엇과 대조하는지 정의하지 않았다. marker가 ZIP 안에 있다는 사실만으로는 runtime과 config의 완전성·동일성을 증명하지 못한다. 기존 backup metadata의 schema/version, ZIP 자체 checksum, 검증 실패 때의 사용 금지 표시도 결정돼야 한다.

## 실패 시나리오 누락

- **원본 디렉터리 삭제 도중 중단되는 경우**가 없다. ZIP 검증 뒤 디렉터리를 재귀 삭제하다 실패하면 ZIP과 일부 디렉터리가 공존한다. 이 상태에서 backup 선택 순서와 retention이 중복분을 어떻게 처리하는지 없으면 잘못된 세대를 삭제하거나 rollback 후보가 비결정적이 된다.

- **rollback의 해제·복원 중 실패**가 다뤄지지 않았다. ZIP을 임시 해제한 뒤 기존 Runtime을 교체하는 도중 실패하면 어느 원본을 이용해 rollback 자체를 rollback하는지, temporary extraction의 정리 실패를 어떻게 격리하는지 필요하다. 배포 실패 복구만 보장하고 rollback 실패 복구를 보장하지 않으면 새 형식이 실제 복구 신뢰성을 낮춘다.

- **config backup 부재/부분 존재의 의미**가 모호하다. 계획은 `필요 시` MPA 관리 설정을 복원한다고 하지만, ZIP과 디렉터리 모두에서 config가 없을 때 허용되는 정상 상태인지, migration이 있었는데 누락된 손상인지 구분하지 않는다. 잘못 분류하면 config를 복원하지 않아 Runtime과 설정 schema가 불일치할 수 있다.

- **동시 deploy/rollback 및 동일 release 재시도**가 고려되지 않았다. attempt-id가 이미 경로 식별에 사용되지만 ZIP 이름·lock·선택 기준은 없다. 두 작업이 retention과 backup discovery를 동시에 실행하면 새 ZIP 또는 임시 디렉터리를 서로 삭제/선택할 위험이 있다.

- **retention 삭제 실패와 권한 오류**가 없다. 성공 배포 후 오래된 ZIP 삭제가 실패할 경우 deploy를 성공으로 둘지 경고로 둘지, receipt에 무엇을 남길지, 다음 실행에서 어떻게 재시도할지 정해야 운영 상태가 관찰 가능하다.

## 구조·정합성 문제

- **architecture의 현재 계약과 계획의 중간 상태가 충돌한다.** architecture는 “성공 marker가 있는 백업 최신 3개”를 디렉터리 경로로 명시한다. 계획의 압축 실패 fallback 디렉터리는 성공한 deploy의 backup이지만 retention에서 제외한다. 이를 architecture 갱신만으로 해결하면 백업의 성공 의미가 형식에 따라 달라지므로, `성공 배포`, `rollback 가능`, `archive 완료`를 분리한 명시적 상태 모델이 필요하다.

- **backup discovery의 호환성 규칙이 빠져 있다.** 새 ZIP과 기존 디렉터리, archive 미완료 디렉터리가 같은 release/timestamp 범위에서 공존할 수 있다. 최신 후보 선정, 명시 선택 시 동명이인 해소, 손상 ZIP fallback 순서가 정의되지 않아 “기존 디렉터리형 backup 호환”은 테스트 한 건으로 보장되지 않는다.

- **수정 대상 문서가 계약 전체를 포괄하지 않는다.** `contracts.md`는 존재하지 않았지만, 계획은 archive format·metadata·receipt·rollback selection이라는 인터페이스 변경을 `deployment-coordination.md`와 architecture에만 남긴다. 코드와 테스트가 의존할 명시적 machine-readable/semantic contract가 없으면 이후 구현이 helper 내부 세부사항에 고정될 가능성이 크다.

- **테스트 계획이 crash consistency와 악성 입력을 빠뜨린다.** 정상/압축 실패/두 rollback/retention만으로는 충분하지 않다. 최소한 partial ZIP publish, ZIP 검증 실패, 원본 삭제 실패, 해제 경로 탈출, 복원 중 실패, config 유무 조합, 동시성 또는 lock 거부, 손상된 최신 후보에서 이전 정상 후보 선택을 검증해야 한다.

## 권고되는 계획 보완

구현 전에 backup metadata에 `format`, `archive_state`, `source backup identity`, runtime/config checksums, 생성·검증 시각을 포함한 상태 전이와, atomic publish·안전 해제·후보 선택·실패 정리 규칙을 확정해야 한다. 그 뒤 압축 실패 fallback의 재시도/운영 경로와 retention의 대상 정의를 문서와 테스트에서 동일하게 고정해야 한다.
