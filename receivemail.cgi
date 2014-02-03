#!/usr/bin/perl -w
use strict;
use CGI::Carp qw(fatalsToBrowser); # エラーメッセージを表示する（しない場合コメントアウト）
use CGI;
use CGI::Session;
use Jcode;
use HTML::Template;
use MIME::WordDecoder;
use MIME::Parser;
require './config.pl';
require './global.pl';
require './vars.pl';
require './mail.pl';
require './post.pl';
require './jcode.pl';

my $cgi;
my %config;
my $msg;
my $session;
my $sid;

my $dbh;
my $forumid = 0;
my $forumname = '';
my $forumnote = '';

#プログラム開始
&main;

##########
# メイン
sub main {
	$cgi = new CGI;
	$msg = '';

	# 設定読み込み
	%config = &config;

	# セッション読み込み
	$session = &readSession(1);
	if (defined $session) {
		# セッション ID
		$sid = $session->id;

		# DB オープン
		$dbh = &connectDB(1);


		# メール投稿確認
		&receiveMail();

		# 現在の画面
		$msg .= &checkOnline($dbh, $session->param('userid'), 'メール投稿確認');

		# 画面表示
		&disp;

		# DB クローズ
		&disconnectDB($dbh);
	}
}

###########
# 画面表示
sub disp {
	# テンプレート読み込み
	my $tmpl = &readTemplate($cgi);

	# 共通テンプレート変数セット
	$msg .= &setCommonVars($tmpl, $session, $dbh);

	# メッセージ（あれば）
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

################
# メール投稿処理
sub receiveMail($) {
	MIME::WordDecoder->default(
		MIME::WordDecoder->new( [
			'*' => sub { jcode(shift)->sjis },
			]
		)
	);
	my $oParse = new MIME::Parser;
	# $oParse->output_dir($config{'pop3'}); 
	$oParse->output_dir($config{'sessiondir'});

	my $oPop = Net::POP3->new($config{'pop3'}, Timeout => 60) or die "Can't not open account.";

	# ログイン
	$oPop->login($config{'pop3_user'}, $config{'pop3_pass'});
	
	my $rhMsg = $oPop->list();		#メッセージIDのハッシュを取得する
	
	my $mailkeyChecked = 0;
	my $successCount = 0;

	foreach my $sMsgId (keys %$rhMsg) {
		my $raCont = $oPop->get($sMsgId);
		my $oEnt = $oParse->parse_data($raCont);
		my $oHead = $oEnt->head;
		my %postData = ();

		# print "\n===============================================\n";
		# print "From:", unmime($oHead->get('From'));
		# print "To	:", unmime($oHead->get('To'));
		# print "Subj:", unmime($oHead->get('Subject'));
		$postData{'subject'} = unmime($oHead->get('Subject'));
		chomp($postData{'subject'});
		my ($mailkeyid, $keystr, $kind, $id, $registuserid) = &checkSubject($postData{'subject'});
		if ($mailkeyid) {
	 		PrnCont(\%postData, $oEnt);
	 		my $success = &registData($postData{'subject'}, $kind, $id, $registuserid, $postData{'body'}, $postData{'file1'}, $postData{'file2'}, $postData{'file3'});

			# 登録成功
			if ($success) {
				$successCount++;
				&doDB($dbh, 'UPDATE mailkeys SET deleteflag=? WHERE mailkeyid=?', ('1', $mailkeyid));
				if ($cgi->param('mailkey') eq $postData{'subject'}) {
					$mailkeyChecked = 1;
				}
			}
		}
		$oPop->delete($sMsgId);
	}

	if ($cgi->param('mailkey')) {
		if ($mailkeyChecked) {
			$msg = '投稿を確認しました。';
		} else {
			if ($successCount) {
				$msg = '投稿を確認できませんでしたが、新しいメッセージが'.$successCount.'件ありました。';
			} else {
				$msg .= '投稿を確認できませんでした。';
			}
		}
	} else {
		$msg = '確認が終了しました。';
		if ($successCount) {
			$msg .= '新しいメッセージが'.$successCount.'件ありました。';
		} else {
			$msg .= '新しいメッセージはありませんでした。';
		}
	}

	# ログオフ
	$oPop->quit;
}

############################
# メールサブジェクトチェック
sub checkSubject() {
	my $subject = shift;
	if ($subject =~ /^post(\d+)_(.+)$/) {
		my $mailkeyid = $1;
		my $keystr = $2;
		my $sql = 
			'SELECT'.
			' a.kind,'.
			' a.id,'.
			' a.registuserid'.
			' FROM'.
			' mailkeys a,'.
			' users b'.
			' WHERE'.
			' a.registuserid=b.userid'.
			' AND a.mailkeyid=?'.
			' AND a.keystr=?'.
			' AND a.deleteflag=?'.
			' AND b.deleteflag=?';
		my @bind = ($mailkeyid, $keystr, '0', '0');
		my ($kind, $id, $registuserid) = &selectFetchArray($dbh, $sql, @bind);
		if ($kind) {
			return ($mailkeyid, $keystr, $kind, $id, $registuserid);
		}
	} else {
		return 0;
	}
}



################################
# メールの内容を確認
sub PrnCont($;$;$) {
	my($postData, $oEnt, $iLvl) = @_;

	$iLvl = 0 unless($iLvl);
	unless ($oEnt->is_multipart) {
		# シングルパート
		# print "SINGLE:", jcode($oEnt->bodyhandle->as_string)->sjis;
		$$postData{'body'} = jcode($oEnt->bodyhandle->as_string)->sjis;
	} else {
		# マルチパート
		my $nCnt = $oEnt->parts;		#Count of Parts
		for (my $i=0; $i<$nCnt;$i++) {
			if($oEnt->parts($i)->is_multipart) {
				#マルチパートのネスト
				# print "PARTS: $i (Nested)\n";
				PrnCont($postData, $oEnt->parts($i), $iLvl+1);
			} else {
				#普通のマルチパート
				# print "--------------------------------------------------\n";
				# print "PART:", ref($oEnt), " LVL:$iLvl\n";
				# print "PATH:", $oEnt->parts($i)->bodyhandle->path, "\n";
				# print "TYPE:", $oEnt->parts($i)->mime_type, "\n";
 				if ($oEnt->parts($i)->mime_type eq "text/plain") {
					# print "TEXT:\n";
					# print jcode($oEnt->parts($i)->bodyhandle->as_string)->sjis, "\n"
					$$postData{'body'} = jcode($oEnt->parts($i)->bodyhandle->as_string)->sjis;
				} elsif($oEnt->parts($i)->mime_type eq "text/html") {
					# print "HTML:\n";
					# print jcode($oEnt->parts($i)->bodyhandle->as_string)->sjis, "\n"
				} else {
					my $sPath = $oEnt->parts($i)->bodyhandle->path();
					# print "--FILES--------------------\n";
					# print "PATH:", $sPath, "\n";
					if (&checkFileExt($sPath)) {
						# ファイル1
						if (!$$postData{'file1'}) {
							$$postData{'file1'} = $sPath;
						# ファイル2
						} elsif (!$$postData{'file2'}) {
							$$postData{'file2'} = $sPath;
						# ファイル3
						} elsif (!$$postData{'file3'}) {
							$$postData{'file3'} = $sPath;
						}
					}
				}
			}
		}
	}
}

################################
# ファイル有効を確認
sub checkFileExt() {
	my $file = shift;
	my $ext = '';
	if ($file =~ m|(\.[^./\\]+)$|) {
		$ext = lc($1);
	}
	if ($ext ne '.jpg' && $ext ne '.jpeg' && $ext ne '.gif' && $ext ne '.png') {
		return 0;
	} else {
		return 1;
	}
}


#######
# 登録
sub registData($) {
	my ($key, $kind, $id, $registuserid, $body, $file1, $file2, $file3) = @_;
	$body =~ s/\r\n/\n/g;
	$body =~ s/^\n+//;
	$body =~ s/\n+$//;
	my $title = '';
	if ($kind eq 'tp') {
		# トピックの入力チェック
		my @mailBody = split("\n", $body);
		chomp(@mailBody);
		$title = shift(@mailBody);
		$body = '';
		foreach (@mailBody) {
			$body .= $_."\n";
		}
		$body =~ s/^\n+//;
		$body =~ s/\n+$//;
		
		# トピックタイトル
		$msg .= &checkString('タイトル', $title, 255, 1);
		if ($msg) {
			return 0;
		}
	}
	# 本文
	if (!$body) {
		$body = '(本文なし)';
	}
	$msg .= &checkString('本文', $body, 2000, 1);
	if ($msg) {
		return 0;
	}

	# 写真1
	my $fname1 = '';
	my $lname1 = '';
	my $sname1 = '';
	if ($file1) {
		my ($lname, $sname) = &attachFile($file1, 1, $key);
		if (!$lname) {
			$msg .= '写真1の種別が不明です。';
			return 0;
		} else {
			$lname1 = $lname;
			$sname1 = $sname;
		}
	}

	# 写真2
	my $fname2 = '';
	my $lname2 = '';
	my $sname2 = '';
	if ($file2) {
		my ($lname, $sname) = &attachFile($file2, 2, $key);
		if (!$lname) {
			$msg .= '写真2の種別が不明です。';
			return 0;
		} else {
			$lname2 = $lname;
			$sname2 = $sname;
		}
	}

	# 写真3
	my $fname3 = '';
	my $lname3 = '';
	my $sname3 = '';
	if ($file3) {
		my ($lname, $sname) = &attachFile($file3, 3, $key);
		if (!$lname) {
			$msg .= '写真3の種別が不明です。';
			return 0;
		} else {
			$lname3 = $lname;
			$sname3 = $sname;
		}
	}

	# トピック登録
	if ($kind eq 'tp') {
		my %data;
		$data{'title'} = $title;
		$data{'body'} = $body;
		$data{'fname1'} = $fname1;
		$data{'lname1'} = $lname1;
		$data{'sname1'} = $sname1;
		$data{'fname2'} = $fname2;
		$data{'lname2'} = $lname2;
		$data{'sname2'} = $sname2;
		$data{'fname3'} = $fname3;
		$data{'lname3'} = $lname3;
		$data{'sname3'} = $sname3;
		$msg .= &submitTopic($dbh, $id, \%data, $registuserid);
		if ($msg) {
			return 0;
		}
	# トピックコメント登録
	} elsif ($kind eq 'tc') {
		my %data;
		$data{'body'} = $body;
		$data{'fname1'} = $fname1;
		$data{'lname1'} = $lname1;
		$data{'sname1'} = $sname1;
		$data{'fname2'} = $fname2;
		$data{'lname2'} = $lname2;
		$data{'sname2'} = $sname2;
		$data{'fname3'} = $fname3;
		$data{'lname3'} = $lname3;
		$data{'sname3'} = $sname3;
		$msg .= &submitTopicComment($dbh, $id, \%data, $registuserid);
		if ($msg) {
			return 0;
		}
	}

	return 1;
}


