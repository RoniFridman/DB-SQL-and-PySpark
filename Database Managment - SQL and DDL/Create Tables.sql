CREATE TABLE Traveler(
    tID int primary key,
        check (tID >= 100000000 AND tID <= 999999999),
    name varchar(50),
    favTripsType varchar(50)
);

CREATE TABLE TravelerInTrip(
    tID int,
    tripName varchar(50),
    startDate date,
    endDate date,
    primary key(tID, tripName, startDate, endDate),
    foreign key (tID) references Traveler
);

CREATE TABLE Friends(
    tID1 int,
    tID2 int,
    primary key(tID1, tID2),
    foreign key (tID1) references Traveler(tID),
    foreign key (tID2) references Traveler(tID)
);