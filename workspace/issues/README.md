# MAP Product Issues

이 폴더는 **source 저장소의 중앙 수집함**이다. 설치 프로젝트에서 발견한 MPA 개선점은 먼저 각 프로젝트의 `workspace/issues/<filename>.md`에 원본으로 기록한다. 사용자가 수집을 요청한 경우에만 source 운영자가 원본을 `inbox/<project-ref>/`로 수집한다.

`inbox/<project-ref>/`의 수집 이슈는 검토 내용을 먼저 사용자에게 제시한다. 사용자가 채택하면 새 task plan을 연결한 뒤, 기각하면 판단 근거를 기록한 뒤 `archived/YYYY/MM/<project-ref>/`로 즉시 이동한다. archive는 이슈의 처리 결정을 보관하는 것이며, 채택된 작업의 구현 완료를 뜻하지 않는다.

이 경로는 Runtime release나 신규 설치 골격에 포함하지 않는다.
