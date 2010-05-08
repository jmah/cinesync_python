<?xml version="1.0" encoding="UTF-8" ?>
<session xmlns="http://www.cinesync.com/ns/session/3.0" version="3" sessionFeatures="standard" userData="sessionUserData blah bloo blee">
    <media>
        <name>024b_fn_079_v01_1-98.mov</name>
		<locators>
			<path>/Volumes/Scratch/test_files/movies/024b_fn_079_v01_1-98.mov</path>
		</locators>
		<playRange>
			<inFrame value="40" />
			<outFrame value="50" />
			<playOnlyRange value="true" />
		</playRange>
    </media>
    <media active="true" currentFrame="65">
        <name>sample_mpeg4.mp4</name>
		<locators>
			<url>http://example.com/test_files/movies/sample_mpeg4.mp4</url>
			<shortHash>e74db5de61fa5483c541a3a3056f22d158b44ace</shortHash>
		</locators>
		<playRange>
			<inFrame value="62" />
			<outFrame value="67" />
			<playOnlyRange value="true" />
		</playRange>
    </media>
    <media userData="myPrivateInfo">
        <name>Test_MH 2fps.mov</name>
		<locators>
			<shortHash>f9f0c5d3e3e340bcc9486abbb01a71089de9b886</shortHash>
		</locators>
		<notes>These notes on the last movie.</notes>
        <annotation frame="1">
			<notes>This is a note on the first frame of the last movie.</notes>
		</annotation>
    </media>
	<notes>These are my session notes.&#x0A;newline.</notes>
</session>
