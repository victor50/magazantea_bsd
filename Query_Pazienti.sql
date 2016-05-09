USE [SpiderCPAntea]
GO

SELECT [IDAna]
      ,[dbo].[fn_GetString]([Cognome]) as Cognome
      ,[dbo].[fn_GetString]([nome]) as Nome
      ,[dbo].[fn_GetString]([CodiceFiscale]) as CodiceFiscale
      ,[DataNascita]
      ,[Sesso]
      ,[dbo].[fn_GetString]([LuogoNascita]) as LuogoNascita
      ,[dbo].[fn_GetString]([Indirizzo]) as Indirizzo
      ,[dbo].[fn_GetString]([Localita]) as Localita
      ,[dbo].[fn_GetString]([CAP]) as CAP
      ,[dbo].[fn_GetString]([Provincia]) as Provincia
      ,[dbo].[fn_GetString]([Telefono]) as Telefono
      ,[dbo].[fn_GetString]([Telefono2]) as Telefono2
      ,[dbo].[fn_GetString]([Cellulare]) as Cellulare
      ,[dbo].[fn_GetString]([Email]) as Email
      ,[Cittadinanza]
      ,[FlagDecesso]
      ,[DataDecesso]
      ,[dbo].[fn_GetString]([NomeCitofono]) as NomeCitofono
      ,[dbo].[fn_GetString]([Municipio]) as Municipio
	  ,[dbo].[fn_GetString]([Quartiere]) as Quartiere
      ,[dbo].[fn_GetString]([Palazzina]) as Palazzina
      ,[dbo].[fn_GetString]([Interno]) as Interno
      ,[dbo].[fn_GetString]([Scala]) as Scala
      ,[dbo].[fn_GetString]([Piano]) as Piano
      ,[FlgAscensore]
      ,[FlgParcheggio]
      ,[dbo].[fn_GetString]([IndirizzoAltraRes]) as IndirizzoAltraRes
      ,[dbo].[fn_GetString]([CapAltraRes]) as CapAltraRes
      ,[dbo].[fn_GetString]([CittaAltraRes]) as CittaAltraRes
      ,[dbo].[fn_GetString]([ProvinciaAltraRes]) as ProvinciaAltraRes
      ,[dbo].[fn_GetString]([ProvinciaNascita]) as ProvinciaNascita
      ,[dbo].[fn_GetString]([DistrettoASL]) as DistrettoASL
  FROM [dbo].[XAR_ANAGRACEN]
GO


