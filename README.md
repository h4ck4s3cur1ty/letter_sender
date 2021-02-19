# letter_sender

최근에 입대한 친한동생, 곧 입대하는 친구를 위해 만든 인터넷편지 매크로 입니다.  
  
## How it works
육군 공식홈페이지 버전(letter_sender_katc.py)과 더캠프 버전(letter_sender_katc.py)이 있습니다.  
    
보안뉴스와 JTBC 기사를 RSS기반으로 기사제목과 내용을 크롤링하며,  
공식홈페이지 버전은 Selenium을 이용하고, 더캠프 버전은 requests를 이용합니다.
  
공식홈페이지는 한 편지당 최대 800자, 더캠프는 최대 1500자를 지원합니다.  
각자 입맛에 맞게 사용하시면 됩니다.  

## Usage

공식홈페이지 버전은 하단에 위치한 다음과 같은 코드를 예시에 따라서 훈련병에 맞게 입력하시면 됩니다.
```
enlistment_date = '180625' # 입대일
birth = '980117' # 생년월일
name = '홍길동' # 성함
letter_password = 'password1234' # 편지 비밀번호
```
  
더캠프 버전은 하단에 위치한 다음과 같은 코드에 더캠프 아이디와 비밀번호를 입력하시면 됩니다.
```
login('userid', 'userpwd')
```
