'use client';
import { SetStateAction, useState } from "react";
import Image from "next/image";
import { Box, Button, Typography, Grid, Card, CardContent, MenuItem, Select, FormControl } from "@mui/material";


type TopicData = {
  [key: string]: { title: string; summary: string }[];
};

const TopicData: TopicData = {
  Technology: [
    { title: "AI Revolution", summary: "Artificial Intelligence is transforming industries worldwide." },
    { title: "Quantum Computing", summary: "The future of computation is here with quantum advancements." },
    { title: "SpaceX Innovations", summary: "SpaceX continues to push the boundaries of space exploration." },
    { title: "Electric Vehicles", summary: "EVs are becoming more accessible and efficient." },
    { title: "5G Technology", summary: "The rollout of 5G networks is accelerating globally." },
    { title: "Cybersecurity Trends", summary: "Protecting digital assets is more critical than ever." },
    { title: "Blockchain Adoption", summary: "More industries are embracing blockchain for transparency." },
    { title: "AR and VR", summary: "Augmented and Virtual Reality are redefining experiences." },
    { title: "Tech Startups", summary: "New players are disrupting traditional markets." },
  ],
  Politics: [
    { title: "Election Updates", summary: "Latest results and analysis from global elections." },
    { title: "Policy Changes", summary: "Governments are introducing new policies worldwide." },
    { title: "International Relations", summary: "Key diplomatic developments and their implications." },
    { title: "Climate Policy", summary: "Nations are debating strategies for climate action." },
    { title: "Economic Reforms", summary: "Major economic shifts in global markets." },
    { title: "Defense Strategies", summary: "Updates on military strategies and alliances." },
    { title: "Protests Worldwide", summary: "Social movements are gaining momentum globally." },
    { title: "Trade Agreements", summary: "Countries are negotiating crucial trade deals." },
    { title: "Leadership Changes", summary: "New leaders are emerging across nations." },
  ],
  Sports: [
    { title: "NBA Finals", summary: "The NBA's biggest games of the season." },
    { title: "NFL Draft", summary: "The NFL's top picks and their impact on the league." },
    { title: "MLB World Series", summary: "The best teams and players in the league." },
    { title: "NHL Stanley Cup", summary: "The NHL's most exciting games and moments." },
    { title: "Formula 1 Races", summary: "The world's most thrilling motorsports events." },
    { title: "UEFA Champions League", summary: "The best teams and players in Europe." },
    { title: "World Cup Finals", summary: "The most exciting matches and moments in soccer." },
    { title: "Tennis Grand Slams", summary: "The best tennis players and tournaments." },
    { title: "World Cup Finals", summary: "The most exciting matches and moments in soccer." },
  ],
  Health: [
    { title: "Medical Breakthroughs", summary: "The latest medical advancements and discoveries." },
    { title: "Mental Health", summary: "The latest research and treatments for mental health." },
    { title: "Vaccine Updates", summary: "The latest vaccines and their impact on public health." },
    { title: "Cancer Research", summary: "The latest breakthroughs in cancer treatment." },
    { title: "COVID-19 Updates", summary: "The latest information on the pandemic." },
    { title: "Nutrition Advice", summary: "The latest dietary recommendations and healthy eating tips." },
    { title: "Fitness Trends", summary: "The latest workout routines and fitness tips." },
    { title: "Medical Devices", summary: "The latest advancements in medical technology." },
    { title: "Mental Health Support", summary: "The latest resources for mental health support." },
  ],
};

export default function Home() {
  const [selectedTopic, setSelectedTopic] = useState("Technology");

  const handleTopicChange = (event: { target: { value: SetStateAction<string>; }; }) => {
    setSelectedTopic(event.target.value);
  };

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        backgroundColor: "#f9f9f9",
        textAlign: "center",
        padding: 2,
      }}
    >
      <FormControl sx={{ marginBottom: 4, width: "150px", height: "40px" }}>
        <Select
          value={selectedTopic}
          onChange={handleTopicChange}
          displayEmpty
          inputProps={{ "aria-label": "Select Topic" }}
        >
          {Object.keys(TopicData).map((topic) => (
            <MenuItem value={topic} key={topic}>
              {topic}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <Typography
        variant="h3"
        component="h1"
        sx={{ marginBottom: 4, color: "#333", fontWeight: "bold" }}
      >
        News Summarizer
      </Typography>

      <Grid container spacing={1} justifyContent="center">
        {TopicData[selectedTopic].map((news, index) => (
          <Grid item xs={4}
            sx={{
              display: "flex",
              justifyContent: "center",
            }}
          key={index}>
            <Card
              sx={{
                maxWidth: 300,
                borderRadius: 2,
                boxShadow: "0 4px 10px rgba(0, 0, 0, 0.1)",
                transition: "transform 0.3s",
                '&:hover': {
                  transform: "scale(1.05)",
                },
              }}
            >
              <CardContent>
                <Typography variant="h6" component="div" sx={{ fontWeight: "bold" }}>
                  {news.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {news.summary}
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  sx={{ marginTop: 2 }}
                  fullWidth
                >
                  Read More
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}