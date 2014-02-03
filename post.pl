use strict;
use CGI::Carp qw(fatalsToBrowser); # エラーメッセージを表示する（しない場合コメントアウト）
use CGI;

require './global.pl';
require './jcode.pl';

# 設定読み込み
my %config = &getConfig;

# 投稿受付
sub postData($) {
	my ($dbh, $id, $kind, $data, $key) = @_;
	my $msg = '';

	if ($kind eq 'tp') {
		# タイトル
		$msg .= &checkString('タイトル', $$data{'title'}, 255, 1);
		if ($msg) {
			return $msg;
		}
		# 本文
		$msg .= &checkString('本文', $$data{'body'}, 2000, 1);
		if ($msg) {
			return $msg;
		}
	}
	if ($kind eq 'tc') {
		# コメント
		$msg .= &checkString('コメント', $$data{'body'}, 2000, 1);
		if ($msg) {
			return $msg;
		}
	}

	
	# 写真1
	my $file1 = $$data{'file1'};
	$$data{'fname1'} = $$data{'file1'}.'';
	$$data{'lname1'} = '';
	$$data{'sname1'} = '';
	if ($file1) {
		my ($lname, $sname) = &uploadFile($$data{'file1'}, 1, $key);
		if (!$lname) {
			$msg .= '写真1の種別が不明です。';
			return $msg;
		} else {
			$$data{'lname1'} = $lname;
			$$data{'sname1'} = $sname;
		}
	}

	# 写真2
	my $file2 = $$data{'file2'};
	$$data{'fname2'} = $$data{'file2'}.'';
	$$data{'lname2'} = '';
	$$data{'sname2'} = '';
	if ($file2) {
		my ($lname, $sname) = &uploadFile($$data{'file2'}, 2, $key);
		if (!$lname) {
			$msg .= '写真2の種別が不明です。';
			return $msg;
		} else {
			$$data{'lname2'} = $lname;
			$$data{'sname2'} = $sname;
		}
	}

	# 写真3
	my $file3 = $$data{'file3'};
	$$data{'fname3'} = $$data{'file3'}.'';
	$$data{'lname3'} = '';
	$$data{'sname3'} = '';
	if ($file3) {
		my ($lname, $sname) = &uploadFile($$data{'file3'}, 3, $key);
		if (!$lname) {
			$msg .= '写真3の種別が不明です。';
			return $msg;
		} else {
			$$data{'lname3'} = $lname;
			$$data{'sname3'} = $sname;
		}
	}

	# 重複チェック
	if ($kind eq 'tp') {
		my @bind = ($id, $$data{'title'}, $$data{'body'}, '0');
		my $count = &selectFetch($dbh, 'SELECT count(*) FROM topics WHERE forumid=? AND title=? AND body=? AND deleteflag=? AND DATE_ADD(registtime, INTERVAL 5 MINUTE) > now()', @bind);
		if ($count) {
			$msg .= '同じトピックを続けて作成できません。';
			return $msg;
		}
	} elsif ($kind eq 'tc') {
		my @bind = ($id, $$data{'body'}, '0');
		my $count = &selectFetch($dbh, 'SELECT count(*) FROM topiccomments WHERE topicid=? AND body=? AND deleteflag=? AND DATE_ADD(registtime, INTERVAL 5 MINUTE) > now()', @bind);
		if ($count) {
			$msg .= '同じコメントを続けて投稿できません。';
			return $msg;
		}
	}

	
	return $msg;
}

#################
# トピックの登録
sub submitTopic($) {
	my ($dbh, $forumid, $data, $userid) = @_;

	my $msg = '';

	# forumid, userid 有効性チェック
	if ($forumid && $userid) {
		my $sql =
			'SELECT count(*)'.
			' FROM'.
			' forums a,'.
			' users b'.
			' WHERE'.
			' a.powerlevel <= b.powerlevel'.
			' AND a.forumid=?'.
			' AND a.deleteflag=?'.
			' AND b.userid=?'.
			' AND b.deleteflag=?';
		my @bind = ($forumid, '0', $userid, '0');
		my $count = &selectFetch($dbh, $sql, @bind);
		if (!$count) {
			$msg .= 'ID が不正です。';
			return $msg;
		}
	} else {
		$msg .= 'ID が不正です。';
		return $msg;
	}
	
	# 重複チェック
	my @bind = ($forumid, $$data{'title'}, $$data{'body'}, '0');
	my $count = &selectFetch($dbh, 'SELECT count(*) FROM topics WHERE forumid=? AND title=? AND body=? AND deleteflag=? AND registtime + 5 * 60 > now()', @bind);
	if ($count) {
		$msg .= '同じトピックを続けて作成できません。';
		return $msg;
	}

	# DB 登録
	my @bind = ($forumid, $$data{'title'}, $$data{'body'}, $userid, $userid);
	my $sql = 
		'INSERT INTO topics('.
		'forumid, '.
		'title, '.
		'body, '.
		'registuserid, '.
		'lastuserid, '.
		'registtime, '.
		'lasttime '.
		') VALUES (?, ?, ?, ?, ?, now(), now())';

	&doDB($dbh, $sql, @bind);
	$$data{'newtopicid'} = &selectFetch($dbh, 'SELECT LAST_INSERT_ID()');
	if (&publishFile($$data{'lname1'}, 'tp'.$$data{'newtopicid'}.'_1')) {
		&publishFile($$data{'sname1'}, 'tp'.$$data{'newtopicid'}.'_1_s');
	}
	if (&publishFile($$data{'lname2'}, 'tp'.$$data{'newtopicid'}.'_2')) {
		&publishFile($$data{'sname2'}, 'tp'.$$data{'newtopicid'}.'_2_s');
	}
	if (&publishFile($$data{'lname3'}, 'tp'.$$data{'newtopicid'}.'_3')) {
		&publishFile($$data{'sname3'}, 'tp'.$$data{'newtopicid'}.'_3_s');
	}

	# 集計
	if (&selectFetch($dbh, 'SELECT count(*) FROM addup WHERE userid=?', $userid)) {
		my $sql = 
			'UPDATE addup SET'.
			' topiccount=topiccount+1'.
			' WHERE'.
			' userid=?';
		my @bind = ($userid);
		&doDB($dbh, $sql, @bind);
	} else {
		my $sql = 
			'INSERT addup ('.
			' userid,'.
			' messagecount,'.
			' topiccount,'.
			' topiccommentcount'.
			') VALUES (?, ?, ?, ?)';
		my @bind = ($userid, 0, 1, 0);
		&doDB($dbh, $sql, @bind);
	}
	
	return $msg;

}

##########################
# トピックコメントの登録
sub submitTopicComment($) {
	my ($dbh, $topicid, $data, $userid) = @_;

	my $msg = '';

	# topicid, userid 有効性チェック
	my $forumid;
	if ($topicid && $userid) {
		my $sql =
			'SELECT a.forumid'.
			' FROM'.
			' forums a,'.
			' topics b,'.
			' users c'.
			' WHERE'.
			' a.forumid=b.forumid'.
			' AND a.powerlevel <= c.powerlevel'.
			' AND a.deleteflag=?'.
			' AND b.topicid=?'.
			' AND b.deleteflag=?'.
			' AND c.userid=?'.
			' AND c.deleteflag=?';
		my @bind = ('0', $topicid, '0', $userid, '0');
		$forumid = &selectFetch($dbh, $sql, @bind);
		if (!$forumid) {
			$msg .= 'ID が不正です。';
			return $msg;
		}
	} else {
		$msg .= 'ID が不正です。';
		return $msg;
	}
	
	# 重複チェック
	my @bind = ($topicid, $$data{'body'}, '0');
	my $count = &selectFetch($dbh, 'SELECT count(*) FROM topiccomments WHERE topicid=? AND body=? AND deleteflag=? AND registtime + 5 * 60 > now()', @bind);
	if ($count) {
		$msg .= '同じコメントを続けて投稿できません。';
		return 0;
	}

	# DB 登録
	my @bind = ($forumid, $topicid, $$data{'body'}, $userid);
	my $sql = 
		'INSERT INTO topiccomments('.
		'forumid, '.
		'topicid, '.
		'body, '.
		'registuserid, '.
		'registtime'.
		') VALUES (?, ?, ?, ?, now())';
	&doDB($dbh, $sql, @bind);
	$$data{'newtopiccommentid'} = &selectFetch($dbh, 'SELECT LAST_INSERT_ID()');
	my $commentcount = &selectFetch($dbh, 'SELECT count(*) FROM topiccomments WHERE deleteflag=? AND topicid=?', ('0', $topicid));
	@bind = ($$data{'newtopiccommentid'}, $userid, $commentcount, $topicid);
	$sql = 'UPDATE topics SET lastcommentid=?, lastuserid=?, lasttime=now(), commentcount=? WHERE topicid=?';
	&doDB($dbh, $sql, @bind);

	if (&publishFile($$data{'lname1'}, 'tc'.$$data{'newtopiccommentid'}.'_1')) {
		&publishFile($$data{'sname1'}, 'tc'.$$data{'newtopiccommentid'}.'_1_s');
	}
	if (&publishFile($$data{'lname2'}, 'tc'.$$data{'newtopiccommentid'}.'_2')) {
		&publishFile($$data{'sname2'}, 'tc'.$$data{'newtopiccommentid'}.'_2_s');
	}
	if (&publishFile($$data{'lname3'}, 'tc'.$$data{'newtopiccommentid'}.'_3')) {
		&publishFile($$data{'sname3'}, 'tc'.$$data{'newtopiccommentid'}.'_3_s');
	}

	# 集計
	if (&selectFetch($dbh, 'SELECT count(*) FROM addup WHERE userid=?', $userid)) {
		my $sql = 
			'UPDATE addup SET'.
			' topiccommentcount=topiccommentcount+1'.
			' WHERE'.
			' userid=?';
		my @bind = ($userid);
		&doDB($dbh, $sql, @bind);
	} else {
		my $sql = 
			'INSERT addup ('.
			' userid,'.
			' messagecount,'.
			' topiccount,'.
			' topiccommentcount'.
			') VALUES (?, ?, ?, ?)';
		my @bind = ($userid, 0, 0, 1);
		&doDB($dbh, $sql, @bind);
	}

	return $msg;

}



1;
