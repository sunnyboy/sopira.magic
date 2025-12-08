import { z } from "zod";

const baseString = z.string().optional();

export const lookupBaseSchema = z.object({
  factory: z.string().min(1, "Factory is required"),
  code: z.string().min(1, "Code is required"),
  name: z.string().min(1, "Name is required"),
  comment: baseString,
  note: baseString,
});

export type LookupBaseFormData = z.infer<typeof lookupBaseSchema>;

export const locationSchema = lookupBaseSchema;
export type LocationFormData = z.infer<typeof locationSchema>;

export const carrierSchema = lookupBaseSchema;
export type CarrierFormData = z.infer<typeof carrierSchema>;

export const driverSchema = lookupBaseSchema;
export type DriverFormData = z.infer<typeof driverSchema>;

export const potSchema = lookupBaseSchema.extend({
  knocks_max: z.coerce.number().min(0).max(25).default(25),
  weight_nominal_kg: z
    .union([z.coerce.number().nullable(), z.string()])
    .optional()
    .transform((val) => {
      if (val === undefined) return undefined;
      if (val === null) return null;
      if (typeof val === "number" && Number.isNaN(val)) return undefined;
      if (typeof val === "string" && val.trim() === "") return undefined;
      if (typeof val === "string") {
        const parsed = Number(val);
        return Number.isNaN(parsed) ? undefined : parsed;
      }
      return val;
    }),
});
export type PotFormData = z.infer<typeof potSchema>;

export const pitSchema = lookupBaseSchema.extend({
  location: z.string().optional(),
  capacity_tons: z
    .union([z.coerce.number().nullable(), z.string()])
    .optional()
    .transform((val) => {
      if (val === undefined) return undefined;
      if (val === null) return null;
      if (typeof val === "number" && Number.isNaN(val)) return undefined;
      if (typeof val === "string" && val.trim() === "") return undefined;
      if (typeof val === "string") {
        const parsed = Number(val);
        return Number.isNaN(parsed) ? undefined : parsed;
      }
      return val;
    }),
  is_active: z.boolean().default(true),
});
export type PitFormData = z.infer<typeof pitSchema>;

export const machineSchema = lookupBaseSchema.extend({
  machine_uuid: z.string().min(1, "Machine UUID is required"),
  firmware_number: baseString,
});
export type MachineFormData = z.infer<typeof machineSchema>;

export type LookupFormValues =
  | LocationFormData
  | CarrierFormData
  | DriverFormData
  | PotFormData
  | PitFormData
  | MachineFormData;

