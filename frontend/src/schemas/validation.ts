import { z } from "zod";

/**
 * Validation schema for Factory entity
 */
export const factorySchema = z.object({
  code: z.string().min(1, "Code is required"),
  name: z.string().min(1, "Name is required"),
  address: z.string().optional(),
  comment: z.string().optional(),
  note: z.string().optional(),
  tags: z.array(z.string()).default([]),
});

export type FactoryFormData = z.infer<typeof factorySchema>;

/**
 * Validation schema for Measurement entity
 */
export const measurementSchema = z.object({
  // Required date/time
  dump_date: z.string().min(1, "Dump date is required"),
  dump_time: z.string().min(1, "Dump time is required"),
  
  // Required foreign keys
  factory: z.union([z.string(), z.number()]).refine(val => val !== "" && val !== 0, "Factory is required"),
  location: z.union([z.string(), z.number()]).refine(val => val !== "" && val !== 0, "Location is required"),
  carrier: z.union([z.string(), z.number()]).refine(val => val !== "" && val !== 0, "Carrier is required"),
  driver: z.union([z.string(), z.number()]).refine(val => val !== "" && val !== 0, "Driver is required"),
  pot: z.union([z.string(), z.number()]).refine(val => val !== "" && val !== 0, "Pot is required"),
  
  // Optional foreign keys
  pit: z.union([z.string(), z.number()]).optional(),
  machine: z.union([z.string(), z.number()]).optional(),
  
  // Basic measurements
  pit_number: z.string().default(""),
  pot_side: z.enum(["FRONT", "BACK", "NONE"]).default("NONE"),
  pot_knocks: z.union([z.number(), z.string()]).default(0),
  pot_knocks_measurement: z.union([z.number(), z.string()]).optional(),
  pot_weight_kg: z.union([z.number(), z.string()]).default(0),
  
  // Temperature values ROI (°C)
  roi_temp_max_c: z.union([z.number(), z.string()]).optional(),
  roi_temp_mean_c: z.union([z.number(), z.string()]).optional(),
  roi_temp_min_c: z.union([z.number(), z.string()]).optional(),
  
  // ROC values (°C)
  roc_value_min_c: z.union([z.number(), z.string()]).optional(),
  roc_value_max_c: z.union([z.number(), z.string()]).optional(),
  
  // Files and graphs
  video_local_file: z.string().optional(),
  photo_local_file: z.string().optional(),
  graph_roc: z.unknown().optional(),
  graph_temp: z.unknown().optional(),
  
  // Notes
  comment: z.string().optional(),
  note: z.string().optional(),
  
  // Tags
  tags: z.array(z.string()).default([]),
});

export type MeasurementFormData = z.infer<typeof measurementSchema>;
