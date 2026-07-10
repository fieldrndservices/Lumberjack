<?xml version='1.0' encoding='UTF-8'?>
<Library LVVersion="26008000">
	<Property Name="NI.Lib.Icon" Type="Bin">*A#!!!!!!!)!"1!&amp;!!!-!%!!!@````]!!!!"!!%!!!(]!!!*Q(C=\&gt;8"=&gt;MQ%!8143;(8.6"2CVM#WJ",7Q,SN&amp;(N&lt;!NK!7VM#WI"&lt;8A0$%94UZ2$P%E"Y.?G@I%A7=11U&gt;M\7P%FXB^VL\`NHV=@X&lt;^39O0^N(_&lt;8NZOEH@@=^_CM?,3)VK63LD-&gt;8LS%=_]J'0@/1N&lt;XH,7^\SFJ?]Z#5P?=F,HP+5JTTF+5`Z&gt;MB$(P+1)YX*RU2DU$(![)Q3YW.YBG&gt;YBM@8'*\B':\B'2Z&gt;9HC':XC':XD=&amp;M-T0--T0-.DK%USWS(H'2\$2`-U4`-U4`/9-JKH!&gt;JE&lt;?!W#%;UC_WE?:KH?:R']T20]T20]\A=T&gt;-]T&gt;-]T?/7&lt;66[UTQ//9^BIHC+JXC+JXA-(=640-640-6DOCC?YCG)-G%:(#(+4;6$_6)]R?.8&amp;%`R&amp;%`R&amp;)^,WR/K&lt;75?GM=BZUG?Z%G?Z%E?1U4S*%`S*%`S'$;3*XG3*XG3RV320-G40!G3*D6^J-(3D;F4#J,(T\:&lt;=HN+P5FS/S,7ZIWV+7.NNFC&lt;+.&lt;GC0819TX-7!]JVO,(7N29CR6L%7,^=&lt;(1M4#R*IFV][.DX(X?V&amp;6&gt;V&amp;G&gt;V&amp;%&gt;V&amp;\N(L@_Z9\X_TVONVN=L^?Y8#ZR0J`D&gt;$L&amp;]8C-Q_%1_`U_&gt;LP&gt;WWPAG_0NB@$TP@4C`%`KH@[8`A@PRPA=PYZLD8Y!#/7SO!!!!!!</Property>
	<Property Name="NI.Lib.SourceVersion" Type="Int">637566976</Property>
	<Property Name="NI.Lib.Version" Type="Str">1.0.0.0</Property>
	<Property Name="NI.LV.All.SourceOnly" Type="Bool">true</Property>
	<Item Name="Core" Type="Folder">
		<Item Name="Layouts" Type="Folder">
			<Item Name="CSVLayout.lvclass" Type="LVClass" URL="../Core/Layouts/CSVLayout.lvclass/CSVLayout.lvclass"/>
			<Item Name="JSONLayout.lvclass" Type="LVClass" URL="../Core/Layouts/JSONLayout.lvclass/JSONLayout.lvclass"/>
			<Item Name="Layout.lvclass" Type="LVClass" URL="../Core/Layouts/Layout.lvclass/Layout.lvclass"/>
			<Item Name="TextLayout.lvclass" Type="LVClass" URL="../Core/Layouts/TextLayout.lvclass/TextLayout.lvclass"/>
		</Item>
	</Item>
	<Item Name="Support" Type="Folder">
		<Item Name="Config" Type="Folder">
			<Item Name="CheckSchemaVerions.vi" Type="VI" URL="../Support/Config/CheckSchemaVerions.vi"/>
			<Item Name="Merge.vi" Type="VI" URL="../Support/Config/Merge.vi"/>
			<Item Name="Resolve.vi" Type="VI" URL="../Support/Config/Resolve.vi"/>
			<Item Name="ValidateAppenderConfigDTO.vi" Type="VI" URL="../Support/Config/ValidateAppenderConfigDTO.vi"/>
			<Item Name="ValidateFileAppenderConfigDTO.vi" Type="VI" URL="../Support/Config/ValidateFileAppenderConfigDTO.vi"/>
			<Item Name="ValidateFilterDTO.vi" Type="VI" URL="../Support/Config/ValidateFilterDTO.vi"/>
			<Item Name="ValidateLumberjackConfigDTO.vi" Type="VI" URL="../Support/Config/ValidateLumberjackConfigDTO.vi"/>
		</Item>
		<Item Name="Enum" Type="Folder">
			<Item Name="DropPolicyFromString.vi" Type="VI" URL="../Support/Enum/DropPolicyFromString.vi"/>
			<Item Name="DropPolicyString.vi" Type="VI" URL="../Support/Enum/DropPolicyString.vi"/>
			<Item Name="FilterModeFromString.vi" Type="VI" URL="../Support/Enum/FilterModeFromString.vi"/>
			<Item Name="FilterModeString.vi" Type="VI" URL="../Support/Enum/FilterModeString.vi"/>
			<Item Name="SeverityFromString.vi" Type="VI" URL="../Support/Enum/SeverityFromString.vi"/>
			<Item Name="SeverityString.vi" Type="VI" URL="../Support/Enum/SeverityString.vi"/>
		</Item>
		<Item Name="File" Type="Folder">
			<Item Name="BaseFolder.vi" Type="VI" URL="../Support/File/BaseFolder.vi"/>
			<Item Name="IsFileNameSafe.vi" Type="VI" URL="../Support/File/IsFileNameSafe.vi"/>
			<Item Name="ISO8601FileName.vi" Type="VI" URL="../Support/File/ISO8601FileName.vi"/>
			<Item Name="PruneSelection.vi" Type="VI" URL="../Support/File/PruneSelection.vi"/>
		</Item>
		<Item Name="Path" Type="Folder">
			<Item Name="ResolveHostRoot.vi" Type="VI" URL="../Support/Path/ResolveHostRoot.vi"/>
		</Item>
		<Item Name="Severity" Type="Folder">
			<Item Name="RankCompare.vi" Type="VI" URL="../Support/Severity/RankCompare.vi"/>
		</Item>
		<Item Name="Store" Type="Folder"/>
		<Item Name="Tag" Type="Folder">
			<Item Name="DefaultSourceTag.vi" Type="VI" URL="../Support/Tag/DefaultSourceTag.vi"/>
			<Item Name="Sanitize.vi" Type="VI" URL="../Support/Tag/Sanitize.vi"/>
		</Item>
	</Item>
	<Item Name="TypeDefs" Type="Folder">
		<Property Name="NI.SortType" Type="Int">3</Property>
		<Item Name="ConfigDTO" Type="Folder">
			<Item Name="AppenderConfigDTO.ctl" Type="VI" URL="../TypeDefs/ConfigDTO/AppenderConfigDTO.ctl"/>
			<Item Name="FileAppenderConfigDTO.ctl" Type="VI" URL="../TypeDefs/ConfigDTO/FileAppenderConfigDTO.ctl"/>
			<Item Name="FilterDTO.ctl" Type="VI" URL="../TypeDefs/ConfigDTO/FilterDTO.ctl"/>
			<Item Name="LumberjackConfigDTO.ctl" Type="VI" URL="../TypeDefs/ConfigDTO/LumberjackConfigDTO.ctl"/>
		</Item>
		<Item Name="Statement.ctl" Type="VI" URL="../TypeDefs/Statement.ctl"/>
		<Item Name="DropPolicy.ctl" Type="VI" URL="../TypeDefs/DropPolicy.ctl"/>
		<Item Name="Filter.ctl" Type="VI" URL="../TypeDefs/Filter.ctl"/>
		<Item Name="FilterMode.ctl" Type="VI" URL="../TypeDefs/FilterMode.ctl"/>
		<Item Name="RelayMode.ctl" Type="VI" URL="../TypeDefs/RelayMode.ctl"/>
		<Item Name="Severity.ctl" Type="VI" URL="../TypeDefs/Severity.ctl"/>
		<Item Name="AppenderConfig.ctl" Type="VI" URL="../TypeDefs/AppenderConfig.ctl"/>
		<Item Name="FileAppenderConfig.ctl" Type="VI" URL="../TypeDefs/FileAppenderConfig.ctl"/>
		<Item Name="RelayAppenderConfig.ctl" Type="VI" URL="../TypeDefs/RelayAppenderConfig.ctl"/>
		<Item Name="LumberjackConfig.ctl" Type="VI" URL="../TypeDefs/LumberjackConfig.ctl"/>
		<Item Name="Snapshot.ctl" Type="VI" URL="../TypeDefs/Snapshot.ctl"/>
	</Item>
</Library>
