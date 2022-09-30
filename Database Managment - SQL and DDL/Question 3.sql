SELECT NumOfTripsPerType.favTripsType, NumOfTripsPerType.tID, MAX(endDate) AS lastReturn
FROM TravelerInTrip,
     (SELECT Traveler.tID, favTripsType, COUNT(*) AS CountNumOfTrips
        FROM Traveler INNER JOIN TravelerInTrip on Traveler.tID = TravelerInTrip.tID
        GROUP BY Traveler.tID,favTripsType) NumOfTripsPerType,
     (SELECT favTripsType, MAX(CountNumOfTrips) AS MaxTrips
        FROM   (SELECT favTripsType, COUNT(*) AS CountNumOfTrips
                FROM Traveler INNER JOIN TravelerInTrip on Traveler.tID = TravelerInTrip.tID
                GROUP BY Traveler.tID,favTripsType) TripsPerType
        GROUP BY favTripsType) MaxNumOfTripsPerType
WHERE (TravelerInTrip.tID = NumOfTripsPerType.tID) AND
      (NumOfTripsPerType.CountNumOfTrips = MaxNumOfTripsPerType.MaxTrips) AND
      (NumOfTripsPerType.favTripsType = MaxNumOfTripsPerType.favTripsType)
GROUP BY NumOfTripsPerType.favTripsType,NumOfTripsPerType.tID;