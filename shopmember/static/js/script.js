var idmsg="아이디를 입력하세요";
var passwdmsg="비밀번호를 입력하세요";
var repasswdmsg="재입력 비밀번호를 입력하세요";
var repasswderror="입력하신 비밀번호가 다릅니다";
var namemsg="이름을 입력하세요";
var telmsg = "전화번호를 입력하세요";
var gendermsg = "성별을 입력하세요";
var emailmsg = "이메일을 입력하세요";
var confirmmsg = "사용할 수 없는 아이디 입니다.";
var addrmsg = "주소를 입력해 주세요";
var addrtmsg = "상세주소를 입력해 주세요"
var iderror = "입력하신 아이디가 없습니다. \n 다시 확인하세요";
var passwderror = "입력하신 비밀번호가 다릅니다. \n 다시 확인하세요";

var qnatitlemsg="문의 제목을 입력하세요";
var qnacontentmsg="문의 내용을 입력하세요";
var modiqnatitlemsg="수정할 제목을 입력해주세요"
var modiqnacontentmsg="수정할 문의사항을 입력해주세요"

var reviewimgerrormsg = "이미지를 입력해 주세요"
var reviewerrormsg = "별점을 입력해 주세요"

var returntitlemsg="반품 글 제목을 입력해 주세요"
var returncontentmsg="반품 글 내용을 입력해 주세요"
var return_img="반품하실 상품의 이미지를 등록해 주세요"

var modireturntitlemsg = "반품 신청 제목을 입력하세요"
var modireturncontentmsg = "반품하는 내용을 입력해주세요"
var modireturnimg = "반품하시려는 상품의 상태를 업로드 해주세요"

var searcherrormsg="검색하실 단어를 입력해주세요"

var addresseeerror="수취인 이름을 입력하세요"
var addresstelerror = "수취인의 전화번호를 입력하세요"

// 회원정보 수정
function modifycheck() {
	if (!modifyform.user_passwd.value) { // 비밀번호 입력을 하지않고 수정을 누를시 메시지 출력
		alert(passwdmsg);
		modifyform.user_passwd.focus();
		return false;
	} else if (modifyform.user_passwd.value != modifyform.user_repasswd.value) { // 비밀번호와 재입력 비밀번호가 일치하지 않을경우 메시지 출력
		alert(repasswderror);
		modifyform.user_passwd.focus();
		return false;
	}
	if (modifyform.user_tel1.value.length < 3 // tel1 이 3자리가 아닐시
			|| modifyform.user_tel2.value.length < 4 // tel2가 3자리 이상이 아닐시
			|| modifyform.user_tel3.value.length < 4) { // tel3가 4자리가 아닐시 메시지출력
		alert(telmsg);
		modifyform.user_tel1.focus();
		return false;
	}
   if(! modifyform.user_addrt.value){
	alert(addrtmsg);
	modifyform.user_addrt.focus();
	return false;
	}
}


// 가입페이지
function signcheck() {
	// 중복확인
	if (!signform.user_id.value) {
      alert(idmsg);
      signform.user_id.focus();
      return false;
      // 비밀번호 입력 안했을경우 메시지 출력   
   }if(signform.userconfirm.value == "0") {
      alert(confirmmsg);
      signform.user_id.focus();
      return false;
   }
   // 아이디 입력 안했을경우 메시지 출력
    else if (!signform.user_passwd.value) {
      alert(passwdmsg);
      signform.user_passwd.focus();
      return false;
      
   } else if (!signform.user_repasswd.value) {
      alert(repasswdmsg);
      signform.user_repasswd.focus();
      return false;
      
      // 비밀번호와 확인 비밀번호가 다를경우 메시지 출력
   } else if (signform.user_passwd.value != signform.user_repasswd.value) {
      alert(repasswderror)
      signform.user_passwd.focus();
      return false;
      // 이름 입력 안했을경우 메시지 출력
   } else if (!signform.user_name.value) {
      alert(namemsg);
      signform.user_name.focus();
      return false;
   }
   // 전화번호 가 재대로 입력 안됬을시 메시지 출력
	if (signform.user_tel1.value.length < 3 
        || signform.user_tel2.value.length < 4
        || signform.user_tel3.value.length < 4 ) {
        alert(telmsg);
        signform.user_tel1.focus();
        return false;
	}
	
	if (!signform.user_email1.value) {
	alert(emailmsg);
      signform.user_email1.focus();
      return false;
   }
   
   if (!signform.user_email2.value) {
	alert(emailmsg);
      signform.user_email2.focus();
      return false;
   }
   
   // 성별 선택 안하면 메시지 출력
   if (!signform.user_gender.value) {
	alert(gendermsg);
      signform.user_gender.focus();
      return false;
   }
   
   if(! signform.user_addr.value){
	alert(addrmsg);
	signform.user_addr.focus();
	return false;
	}
	if(! signform.user_addrt.value){
	alert(addrtmsg);
	signform.user_addrt.focus();
	return false;
	}

}

function useridconfirm() {
	$.ajax(
		{	// json 영역
			type : "GET",
			url : "confirm",
			data : 	{//시리얼라이즈
				user_id : $("input[name=user_id]").val() // 아이디 값만
			},
			dataType : "text",
			success : function(data) {
				$("#confirmcheck").html(data);
				if(data.indexOf('사용할 수 있는') != -1){
					signform.userconfirm.value = "1";
				} else {
					signform.userconfirm.value = "0";
				}
			},
			error : function(error) {
				// 실패
				$("#confirmcheck").html(error); // error 출력
			}
		}
	);
}
// 로그인 아이디 비번 미입력 체크
function logincheck() {
	if(! loginform.user_id.value){
		alert(idmsg);
		loginform.user_id.focus();
		return false;
	} else if (! loginform.user_passwd.value) {
		alert(passwdmsg);
		loginform.passwd.focus();
		return false;
	}
}

// 전화번호 오토포커스
function nexttel1() {
	if(signform.user_tel1.value.length == 3){
		signform.user_tel2.focus();
	}
}
function nexttel2() {
	if(signform.user_tel2.value.length == 4){
		signform.user_tel3.focus();
	}
}
function nexttel3() {
	if(signform.user_tel3.value.length == 4){
		signform.user_gender.focus();
	}
}

function deletecheck() {
	if(! deleteform.user_passwd.value) {
		alert(passwdmsg);
		loginform.passwd.focus();
		return false;
	}
}

//Q&A 글 수정부분 미기입체크
function modifyprocheck(){
   if(! modifypro.qnatitle.value) {
      alert(modiqnatitlemsg);   //제목
      modifypro.qnatitle.focus();
      return false;
      
   }else if (! modifypro.qnacontent.value) {
      alert(modiqnacontentmsg);   //글내용
      modifypro.qnacontent.focus();
      return false;
	}
}


//Q&A 글 작성
function qnawritecheck() {
   if( ! qnawriteform.user_id.value){
      alert(idmsg); //id
      qnawriteform.user_id.focus();
      return false;
   }else if(! qnawriteform.qnatitle.value) {
      alert(qnatitlemsg);   //제목
      qnawriteform.qnatitle.focus();
      return false;
   }else if (! qnawriteform.qnacontent.value) {
      alert(qnacontentmsg);   //글내용
      qnawriteform.qnacontent.focus();
      return false;
   }else if (! qnawriteform.passwd.value) {
      alert(passwdmsg);   //비밀번호
      qnawriteform.passwd.focus();
      return false;
   }
}

// 리뷰 이미지 없을 시 에러표시
function reviewcheck() {
	if( ! reviewform.reviewimg.value) {
		alert(reviewimgerrormsg);
		return false;
	}
    if(rating.rate == 0){
         alert('별점을 선택해 주세요');
         return false;
     }
}

// 리뷰 수정부분
function reviewmodifycheck() {
	if( ! reviewmodifyform.reviewimg.value) {
		alert(reviewimgerrormsg);
		return false;
	}
    if(rating.rate == 0){
         alert('별점을 선택해 주세요');
         return false;
     }
}

// 반품글 작성
function returncheck() {
	if(! returnform.return_title.value) {
		alert(returntitlemsg);
		returnform.return_title.focus();
		return false;
	}
	if (! returnform.return_content.value){
		alert(returncontentmsg);
		return false;
	}
	if (! returnform.return_img.value){
		alert(return_img);
		return false;
	}
}

// 반품글 수정
function rtmodifyprocheck(){
   if(! returnmodifypro.return_title.value) {
      alert(modireturntitlemsg);   //제목
      returnmodifypro.return_title.focus();
      return false;
      
   }
   if (! returnmodifypro.return_content.value) {
      alert(modireturncontentmsg);   //글내용
      return false;
   }
   if (! returnmodifypro.return_img.value){
      alert(modireturnimg);
      return false;
   }
}

// 검색 오류 표시
function searchcheck() {
	if( ! searchnone.product.value || searchnone.product.value==" ") {
		alert(searcherrormsg);
		return false;
	}
}


// 주문 수정
function ordermodifypro() {
	if(! ordermodifypro.addressee.value ) {
		alert(addresseeerror);
		return false;
	} else if (! ordermodifypro.addressee.value ) {
		alert (addresstelerror);
		return false;
	} else if (! ordermodifypro.user_addr.value ) {
		alert (addrmsg);
		return false;
	} else if (! ordermodifypro.user_addrt.value ) {
		alert (addrtmsg);
		return false;
	}
}